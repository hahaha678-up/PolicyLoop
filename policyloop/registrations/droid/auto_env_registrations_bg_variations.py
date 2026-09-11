# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os

import policyloop.constants
from policyloop.constants import BACKGROUND_ASSET_DIR, DEFAULT_TASK_SUBFOLDERS

"""
Scene registration for TASK × BACKGROUND matrix experiments.

Registers one env per (task, background) combination — i.e. given N tasks and
M backgrounds, you end up with N*M registered envs (BananaInBowlTask_bg_warehouse,
BananaInBowlTask_bg_billiard_hall, ... RubiksCubeAndBananaTask_bg_warehouse, ...).

For per-task random backgrounds (one randomly sampled bg per task, NOT a full
sweep), use `auto_register_droid_envs(randomize_background=True)` from
auto_env_registrations_jointpos.py instead. See docs/background.md → "Choosing a
Background Strategy" for the full comparison.
"""

# Background files to use for variation experiments
BACKGROUND_FILES = [
    "empty_warehouse.hdr",
    "brown_photostudio.hdr",
    "billiard_hall.hdr",
    "home_office.exr",
]

# Tasks to create environments for
TARGET_TASKS = [
    "BananaInBowlTask",
    "RubiksCubeAndBananaTask",
]

def auto_register_droid_envs_bg_variations(
    task_dirs=DEFAULT_TASK_SUBFOLDERS,
    lighting_intensity=500,
    backgrounds: list[str] = None,
    tasks: list[str] = None
):
    """Automatically discover and register task environments with background variations.

    Creates environments for each combination of task and background file.
    Environment names follow the pattern: TaskName_bg_background-name

    Args:
        task_dirs: List of task subdirectories to search for task files.
        lighting_intensity: Intensity for the background dome light.
        backgrounds: List of background filenames. If None, uses BACKGROUND_FILES.
        tasks: List of task names. If None, uses TARGET_TASKS.
    """
    from policyloop.core.environments.factory import batch_create_env_cfgs
    from policyloop.core.observations.observation_utils import generate_image_obs_from_cameras, generate_obs_cfg
    from policyloop.registrations.droid.camera_presets import WRIST_LEFT
    from policyloop.robots.droid import (
        DroidCfg,
        DroidJointPositionActionCfg,
        ProprioceptionObservationCfg,
        WristCameraCfg,
        contact_gripper,
    )
    from policyloop.variations.backgrounds import find_and_generate_background_config
    from policyloop.variations.camera import EgocentricMirroredCameraCfg

    # Use defaults if not provided
    if backgrounds is None:
        backgrounds = BACKGROUND_FILES
    if tasks is None:
        tasks = TARGET_TASKS

    print(f"Registering background variation environments for tasks: {tasks}")
    print(f"Using {len(backgrounds)} backgrounds: {backgrounds}")

    cameras = WRIST_LEFT
    # WristCameraCfg is robot-mounted (wrist_cam is already attached via DroidCfg).
    # Including it as a scene mixin breaks spawn ordering (wrist_cam before robot).
    scene_cameras = [c for c in cameras if c is not WristCameraCfg]

    # Generate Observations
    ImageObsCfg = generate_image_obs_from_cameras(cameras)
    ViewportCameraCfg = generate_image_obs_from_cameras([EgocentricMirroredCameraCfg])
    ObservationCfg = generate_obs_cfg({
        "image_obs": ImageObsCfg(),
        "proprio_obs": ProprioceptionObservationCfg(),
        "viewport_cam": ViewportCameraCfg()
    })

    # Create environments for each background using batch_create_env_cfgs
    all_registered_envs = {}
    for bg_file in backgrounds:
        try:
            # Generate background config
            bg_config = find_and_generate_background_config(
                filename=bg_file,
                folder_path=BACKGROUND_ASSET_DIR,
                intensity=lighting_intensity
            )

            # Create a clean name from the background filename
            bg_name = os.path.splitext(bg_file)[0].replace("_2k", "")
            env_postfix = f"_bg_{bg_name}"

            # Create environments for all tasks with this background
            registered_envs = batch_create_env_cfgs(
                tasks=tasks,
                task_subdirs=task_dirs,  # Search only in specified subdirectories
                tags=["background_variations"],
                env_postfix=env_postfix,
                observations_cfg=ObservationCfg(),
                actions_cfg=DroidJointPositionActionCfg(),
                robot_cfg=DroidCfg,
                camera_cfg=[*scene_cameras, EgocentricMirroredCameraCfg],
                background_cfg=bg_config,
                contact_gripper=contact_gripper,
                dt=1 / (60 * 2),
                render_interval=8,
                decimation=8,
                seed=1,
            )

            # Merge into all_registered_envs
            for task_name, env_cfg_class in registered_envs.items():
                env_key = f"{task_name}_{env_postfix}"
                all_registered_envs[env_key] = env_cfg_class
                if policyloop.constants.VERBOSE:
                    print(f"  Registered: {env_key}")

        except FileNotFoundError as e:
            print(f"Warning: {e}, skipping background '{bg_file}'.")

    print(f"Registered {len(all_registered_envs)} background variation environments.")

    if policyloop.constants.VERBOSE:
        from policyloop.core.environments.factory import print_env_table
        print_env_table()

    return all_registered_envs
