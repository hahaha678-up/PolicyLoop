# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Default registrations must cover exactly the eight bundled tasks."""

import gymnasium as gym
import pytest

import policyloop.core.environments.factory as factory
from policyloop.constants import TASK_DIR
from policyloop.registrations.droid.auto_env_registrations_jointpos import auto_register_droid_envs
from policyloop.registrations.droid.auto_env_registrations_abs_ik import auto_register_droid_abs_ik_envs
from policyloop.registrations.droid.auto_env_registrations_rel_ik import auto_register_droid_rel_ik_envs
from policyloop.registrations.example.auto_env_registration import auto_register_example_envs_franka
from tests.test_repository_boundary import TASK_SCENES


@pytest.fixture
def isolated_registry(monkeypatch):
    monkeypatch.setattr(factory, "_global_factory", factory.EnvFactory(TASK_DIR))
    original = gym.envs.registry.copy()
    yield factory.get_global_env_factory()
    gym.envs.registry.clear()
    gym.envs.registry.update(original)


@pytest.mark.parametrize("register,postfix", [
    (auto_register_droid_envs, ""),
    (auto_register_droid_abs_ik_envs, ""),
    (auto_register_droid_rel_ik_envs, ""),
    (auto_register_example_envs_franka, "FrankaJointPosition"),
])
def test_default_registrations_cover_exact_task_set(isolated_registry, register, postfix):
    register()
    assert set(isolated_registry.get_all_task_names()) == set(TASK_SCENES)
    expected = {name + postfix for name in TASK_SCENES}
    assert set(factory.get_envs()) == expected
    assert expected <= set(gym.envs.registry)


def test_no_duplicate_registrations(isolated_registry):
    auto_register_droid_envs()
    first = set(factory.get_envs())
    auto_register_droid_envs()
    assert set(factory.get_envs()) == first == set(TASK_SCENES)


def test_registered_entry_points_resolve_to_current_package(isolated_registry):
    import importlib
    from policyloop.core.environments.env import PolicyLoopEnv

    auto_register_droid_envs()
    for name in factory.get_envs():
        module_name, class_name = gym.spec(name).entry_point.split(":")
        assert module_name.startswith("policyloop.")
        assert getattr(importlib.import_module(module_name), class_name) is PolicyLoopEnv
