# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from policyloop.constants import DEFAULT_TASK_SUBFOLDERS
from policyloop.core.environments.factory import EnvFactory


def test_standard_registrations_use_benchmark_only():
    assert DEFAULT_TASK_SUBFOLDERS == ["benchmark"]


def test_explicit_task_resolves_from_custom_directory(tmp_path, monkeypatch):
    task_file = tmp_path / "custom_tasks" / "sample.py"
    task_file.parent.mkdir()
    task_file.write_text("class SampleTask:\n    pass\n")

    monkeypatch.setattr(
        "policyloop.core.task.task_utils.get_task_class_name_from_file",
        lambda path: "SampleTask",
    )
    factory = EnvFactory(task_dir=tmp_path)
    resolved = []

    def fake_create_env_cfg(task, **kwargs):
        resolved.append((task, kwargs))
        return object

    monkeypatch.setattr(factory, "create_env_cfg", fake_create_env_cfg)
    generated = factory.auto_discover_and_create_cfgs(
        tasks="SampleTask",
        task_subdirs=["custom_tasks"],
        add_tags="custom",
        env_postfix="DroidJointPosition",
    )

    assert generated == {"SampleTask": object}
    assert Path(resolved[0][0]) == task_file
    assert resolved[0][1] == {
        "tags": "custom",
        "env_prefix": "",
        "env_postfix": "DroidJointPosition",
    }
