"""Check command-line task selection without starting a second simulator."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from isaaclab.app import AppLauncher

import policyloop.constants as constants
import policyloop.core.environments.factory as factory
from policyloop.registrations.droid.auto_env_registrations_bg_variations import BACKGROUND_FILES
from tests.test_registered_envs import isolated_registry
from tests.test_repository_boundary import TASK_SCENES


@pytest.mark.parametrize("script,selected,expected", [
    ("run.py", [], set(TASK_SCENES)),
    ("run.py", ["RubiksCubeLeftOfBowlTask"], {"RubiksCubeLeftOfBowlTask"}),
    ("run_background_variation.py", [], {"BananaInBowlTask", "RubiksCubeAndBananaTask"}),
    ("run_background_variation.py", ["RubiksCubeLeftOfBowlTask"], {"RubiksCubeLeftOfBowlTask"}),
    ("run_background_variation.py", list(TASK_SCENES), set(TASK_SCENES)),
])
def test_runner_registers_selected_tasks(script, selected, expected, isolated_registry, monkeypatch):
    def existing_app(args):
        return SimpleNamespace(app=None)

    existing_app.add_app_launcher_args = AppLauncher.add_app_launcher_args
    monkeypatch.setattr("isaaclab.app.AppLauncher", existing_app)
    for name in ("ENABLE_SUBTASK_PROGRESS_CHECKING", "RECORD_IMAGE_DATA", "VERBOSE", "DEBUG"):
        monkeypatch.setattr(constants, name, getattr(constants, name))
    path = Path(constants.PACKAGE_DIR) / "policies/pi0_family" / script
    monkeypatch.setattr(sys, "argv", [str(path)] + (["--task", *selected] if selected else []))
    runpy.run_path(str(path))
    assert set(isolated_registry.get_all_task_names()) == expected
    if script == "run_background_variation.py":
        envs = {task + "_bg_" + Path(bg).stem for task in expected for bg in BACKGROUND_FILES}
    else:
        envs = expected
    assert set(factory.get_envs()) == envs
