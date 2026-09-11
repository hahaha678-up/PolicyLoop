"""Exercise all bundled scenes and tasks without requiring a policy server."""

import math
from pathlib import Path

import pytest
import torch

import policyloop.constants as constants
import policyloop.core.environments.factory as factory
from policyloop.core.environments.runtime import create_env, end_episode
from policyloop.core.task.event_tracker import EventTracker
from policyloop.core.task.subtask_state_machine import SubtaskStateMachine
from policyloop.registrations.droid.auto_env_registrations_jointpos import auto_register_droid_envs
from tests.test_repository_boundary import SCENES, TASK_SCENES
from tests.test_registered_envs import isolated_registry


def _exercise(env_name, check_task):
    env, cfg = create_env(env_name, num_envs=1, use_fabric=True)
    try:
        obs, _ = env.reset()
        assert obs is not None
        state = None
        if check_task:
            assert cfg.subtasks
            state = SubtaskStateMachine(
                env=env, env_id=0, subtasks=cfg.subtasks,
                objects_in_scene=list(env.scene.rigid_objects),
            )
            tracker = EventTracker(num_envs=1, device=env.device)
        for _ in range(5):
            actions = torch.cat([
                env.scene["robot"].data.joint_pos[:, :7],
                torch.zeros((1, 1), device=env.device),
            ], dim=-1)
            obs, _, term, trunc, _ = env.step(actions)
            assert obs is not None
            assert term.shape == trunc.shape == (1,)
            assert torch.isfinite(env.scene["robot"].data.joint_pos).all()
            if state is not None:
                intended = (set(state.conditionals_state_machine.subtask.group_names)
                            if state.conditionals_state_machine else set())
                events = tracker.check_events(env, [intended], frozen_mask=env._frozen_envs)
                local = [(msg, status) for msg, status, mask in events if mask[0].item()]
                assert len(state.step(env_events=local)) == 4
                score = state.get_total_score()
                assert math.isfinite(score) and 0 <= score <= 1
        env.sim.render()
        cameras = []
        for name, sensor in env.scene.sensors.items():
            output = getattr(sensor.data, "output", {})
            if "rgb" in output:
                rgb = output["rgb"]
                assert torch.isfinite(rgb).all() and rgb[..., :3].max() > 0, name
                cameras.append(name)
        assert len(cameras) == 3
        if state is not None:
            state.reset()
            assert state.current_subtask_index == 0
        end_episode(env)
    finally:
        env.close()


@pytest.fixture
def runtime_output(tmp_path, monkeypatch, isolated_registry):
    if not torch.cuda.is_available():
        pytest.skip("CUDA required for simulation")
    monkeypatch.setattr(constants, "ENABLE_SUBTASK_PROGRESS_CHECKING", True)
    monkeypatch.setattr(constants, "_output_dir", str(tmp_path))


@pytest.mark.parametrize("name", sorted(TASK_SCENES))
def test_task_runtime(name, runtime_output):
    auto_register_droid_envs(task=name)
    _exercise(factory.get_envs(task=name)[0], check_task=True)


@pytest.mark.parametrize("scene", sorted(SCENES))
def test_scene_runtime(scene, tmp_path, runtime_output):
    path = str(Path(constants.SCENE_DIR) / scene)
    source = f"""
from dataclasses import dataclass
import isaaclab.envs.mdp as mdp
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass
from policyloop.core.task.task import Task
from policyloop.core.scenes.utils import import_scene_and_contact_object_list

@configclass
class SmokeTerminations:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)

@dataclass
class SceneRuntimeCheck(Task):
    scene, contact_object_list = import_scene_and_contact_object_list({path!r})
    terminations = SmokeTerminations
    instruction = "Scene runtime verification"
    episode_length_s = 30
    attributes = ["smoke"]
"""
    task_file = tmp_path / "scene_runtime.py"
    task_file.write_text(source)
    auto_register_droid_envs(task=str(task_file), task_dirs=None)
    _exercise(factory.get_envs(task="SceneRuntimeCheck")[0], check_task=False)
