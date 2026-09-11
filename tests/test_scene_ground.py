# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Keep the five bundled scenes at their authored ground heights.

The ground supports the task table; changing it also moves the workspace
relative to robot observations and recorded trajectories.
"""

import glob
import os

import pytest
from pxr import Usd, UsdGeom

from policyloop.constants import SCENE_DIR

CANONICAL_GROUND_Z = -0.697

# These two retained scenes use a different authored ground height.
LEGACY_GROUND_Z = {
    "bananas_5_grey_bin.usda": -0.65,
    "rubiks_cube_banana_bowl.usda": -0.65,
}


def _scene_files() -> list[str]:
    return sorted(glob.glob(os.path.join(SCENE_DIR, "*.usd*")))


def _authored_ground_z(usd_path: str) -> float | None:
    stage = Usd.Stage.Open(usd_path)
    default_prim = stage.GetDefaultPrim()
    if not default_prim.IsValid():
        return None
    ground = stage.GetPrimAtPath(default_prim.GetPath().AppendChild("GroundPlane"))
    if not ground.IsValid():
        return None
    transform = UsdGeom.Xformable(ground).ComputeLocalToWorldTransform(Usd.TimeCode.Default())
    return float(transform.ExtractTranslation()[2])


def test_every_scene_authors_locked_ground():
    scene_files = _scene_files()
    assert scene_files, f"no scenes found under {SCENE_DIR}"
    missing = []
    wrong = []
    for usd_path in scene_files:
        name = os.path.basename(usd_path)
        expected_z = LEGACY_GROUND_Z.get(name, CANONICAL_GROUND_Z)
        ground_z = _authored_ground_z(usd_path)
        if ground_z is None:
            missing.append(name)
        elif ground_z != pytest.approx(expected_z, abs=1e-6):
            wrong.append(f"{name}: {ground_z} (expected {expected_z})")
    assert not missing, f"scenes without /GroundPlane: {missing}"
    assert not wrong, f"scenes with wrong ground height: {wrong}"
