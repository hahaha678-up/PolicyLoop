# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
PolicyLoop - Robot policy integration and parallel closed-loop evaluation.
"""

__version__ = "0.1.0"

# Import constants module to make it available at package level
from . import constants

# Import main modules to make them available at package level
# Use try-except to handle missing dependencies gracefully
try:
    from . import core
except ImportError:
    core = None

try:
    from . import robots
except ImportError:
    robots = None

try:
    from . import observations
except ImportError:
    observations = None

try:
    from . import tasks
except ImportError:
    tasks = None

try:
    from . import inference
except ImportError:
    inference = None

__all__ = [
    "constants",
    "core",
    "robots",
    "observations",
    "tasks",
    "inference",
]