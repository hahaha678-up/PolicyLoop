# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import policyloop.constants
from policyloop.constants import TASK_DIR
from policyloop.core.environments.factory import auto_discover_and_create_cfgs

# camera observations only
from policyloop.core.observations.example import CameraObservationCfg
from policyloop.core.observations.observation_utils import generate_image_obs_from_cameras, generate_obs_cfg
from policyloop.variations.backgrounds import HomeOfficeBackgroundCfg

# variations
from policyloop.variations.camera import (
    EgocentricMirroredCameraCfg,
    EgocentricMirroredWideAngleCameraCfg,
    EgocentricWideAngleCameraCfg,
)
from policyloop.variations.lighting import SphereLightCfg

subdir_tags = {'benchmark': "benchmark"}

camera_cfgs = [EgocentricWideAngleCameraCfg, EgocentricMirroredWideAngleCameraCfg, EgocentricMirroredCameraCfg]

def auto_register_example_envs_droid():
    """Automatically discover and register all available tasks."""

    from policyloop.robots.droid import DroidCfg, DroidJointPositionActionCfg, contact_gripper

    # Generate Observations
    ImageObsCfg = generate_image_obs_from_cameras(camera_cfgs)
    ObservationCfg = generate_obs_cfg({"image_obs": ImageObsCfg()})

    for subdir, tag in subdir_tags.items():

        # Auto-discover and create environments for all task files
        _ = auto_discover_and_create_cfgs(
            task_dir=TASK_DIR,
            task_subdirs=[subdir],
            add_tags=[tag],
            pattern="*.py",
            env_prefix="",
            env_postfix="DroidJointPosition",
            observations_cfg=ObservationCfg(),
            actions_cfg=DroidJointPositionActionCfg(),
            robot_cfg=DroidCfg,
            camera_cfg=camera_cfgs,
            lighting_cfg=SphereLightCfg,
            background_cfg=HomeOfficeBackgroundCfg,
            contact_gripper=contact_gripper,
            dt=1 / (60 * 2),
            render_interval=8,
            decimation=8,
            seed=1,
        )

    from policyloop.core.environments.factory import print_env_table
    print_env_table()

def auto_register_example_envs_franka():
    """Automatically discover and register all available tasks."""

    from policyloop.robots.franka import FrankaCfg, FrankaJointPositionActionCfg, contact_gripper

    # Generate image observation group
    ImageObsCfg = generate_image_obs_from_cameras(camera_cfgs)

    # Create observation configuration with image observations
    ObservationCfg = generate_obs_cfg({
        "image_obs": ImageObsCfg()
    })

    for subdir, tag in subdir_tags.items():

        # Auto-discover and create environments for all task files
        _ = auto_discover_and_create_cfgs(
            task_dir=TASK_DIR,
            task_subdirs=[subdir],
            add_tags=[tag],
            pattern="*.py",
            env_prefix="",
            env_postfix="FrankaJointPosition",
            observations_cfg=ObservationCfg(),
            actions_cfg=FrankaJointPositionActionCfg(),
            robot_cfg=FrankaCfg,
            camera_cfg=camera_cfgs,
            lighting_cfg=SphereLightCfg,
            background_cfg=HomeOfficeBackgroundCfg,
            contact_gripper=contact_gripper,
            dt=1 / (60 * 2),
            render_interval=8,
            decimation=8,
            seed=1,
        )

    from policyloop.core.environments.factory import print_env_table
    print_env_table()
