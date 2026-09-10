# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# isort: skip_file

"""Pytest configuration for RoboLab install-verification tests.

Boots Isaac Sim once at conftest load so test files can freely import
isaaclab/robolab modules at their top level. Auto-accepts the Omniverse
EULA so a fresh install works headless without any prompts.
"""

import os

# Accept the Omniverse EULA non-interactively. Must be set before any
# isaaclab import. setdefault → user can still override.
os.environ.setdefault("OMNI_KIT_ACCEPT_EULA", "Y")

import cv2  # noqa: E402, F401  must be imported before isaaclab
# Initialize PyTorch before Kit extensions alter the Python import environment.
import torch._dynamo  # noqa: E402, F401

from isaaclab.app import AppLauncher  # noqa: E402

# Launch Isaac Sim once for the whole pytest session. Carb's logger is told to
# only emit warnings or worse so install-verification output isn't drowned in
# Isaac Sim's [Info] startup/shutdown chatter.
_launcher = AppLauncher(
    headless=True,
    enable_cameras=True,
    fast_shutdown=False,
    kit_args=os.environ.get("ROBOLAB_KIT_ARGS", ""),
    carb_settings={
        "/log/level": "warn",
        "/log/outputStreamLevel": "warn",
        "/log/fileLogLevel": "warn",
    },
)
simulation_app = _launcher.app


def pytest_addoption(parser):
    parser.addoption(
        "--task",
        default="BananaInBowlTask",
        help="Task class name for test_run_empty (default: BananaInBowlTask). "
             "The test runs the first registered env matching this task.",
    )
    parser.addoption(
        "--env-name",
        default=None,
        help="Full registered env name for test_run_empty (e.g. BananaInBowlTask). "
             "If set, overrides --task.",
    )


import pytest


@pytest.fixture(autouse=True)
def isolated_test_output(tmp_path, monkeypatch):
    """Keep simulation logs separate from saved experiment output."""
    import robolab.constants as constants
    monkeypatch.setattr(constants, "_output_dir", str(tmp_path))


@pytest.fixture
def task_arg(request):
    return request.config.getoption("--task")


@pytest.fixture
def env_name_arg(request):
    return request.config.getoption("--env-name")


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    """Print pytest's summary, then close native plugins with the test exit code."""
    yield
    status = int(session.exitstatus)
    try:
        simulation_app.close()
    except Exception:
        import traceback
        traceback.print_exc()
        status = status or 1
    finally:
        # Kit unloads native plugins during close; a second interpreter teardown
        # can access those unloaded libraries. Preserve pytest's result directly.
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(status)
