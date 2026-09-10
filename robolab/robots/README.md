# Built-in Robots

This is the canonical list of robot embodiments that ship with RoboLab. For how to *use* a robot
(registration wiring, defining your own robot, contact grippers, wrist cameras), see
[`docs/robots.md`](../../docs/robots.md).

| | Robot | Embodiment | Action spaces | Cameras |
|---|-------|------------|---------------|---------|
| <img src="../../docs/images/robots/droid.png" width="480"> | **DROID**<br>(Franka + Robotiq 2F-85)<br>`droid.py` | `single-arm` `fixed-base` `parallel-jaw` | joint position, absolute EE IK, relative EE IK | wrist |
| <img src="../../docs/images/robots/franka.png" width="480"> | **Franka Panda**<br>`franka.py`, `franka_high_pd.py` | `single-arm` `fixed-base` `parallel-jaw` | joint position, absolute EE IK, relative EE IK | — |

Gripper convention for all binary gripper actions: a scalar per gripper, `> 0.5` closes, `≤ 0.5` opens.
Quaternions are `(w, x, y, z)`; absolute IK targets are expressed in the robot root frame, translations in meters.

---

## DROID (Franka + Robotiq 2F-85)

`tags: single-arm · fixed-base · parallel-jaw · wrist-cam · gravity-disabled · high-PD · benchmark-default`

The default benchmark embodiment: a Franka Panda arm with a Robotiq 2F-85 gripper, matching the
[DROID](https://droid-dataset.github.io/) platform. High PD gains (400/80) with gravity disabled on the
arm, plus a 720p wrist camera whose intrinsics are calibrated to match pi05 training data.

| Action config | Layout | Dim |
|---------------|--------|-----|
| `DroidJointPositionActionCfg` | 7 arm joint targets + binary gripper | 8 |
| `DroidIKActionCfg` | absolute EE pose `(x, y, z, qw, qx, qy, qz)` + binary gripper | 8 |
| `DroidRelIKActionCfg` | relative EE pose `(dx, dy, dz, droll, dpitch, dyaw)` + binary gripper | 7 |

- **Config classes:** `DroidCfg` (robot + wrist camera + EE frame transformers)
- **Proprioception:** `ProprioceptionObservationCfg` — arm joint positions, gripper open fraction,
  EE pose (both the gripper mount flange `ee_*` and the rotated control frame `eef_*`)
- **Contact gripper:** `{"gripper": ...left_inner_finger}`
- **Registrations:** `robolab/registrations/droid/` (jointpos, abs-IK, rel-IK, lighting/background variations)

```python
from robolab.robots.droid import DroidCfg, DroidJointPositionActionCfg, contact_gripper
```

## Franka Panda

`tags: single-arm · fixed-base · parallel-jaw`

A stock Franka Panda with its factory finger gripper. Two articulation variants share the same action
configs: `franka.py` with standard PD gains (80/4), and `franka_high_pd.py` with high gains (400/80)
and gravity disabled (better target tracking for policy control).

| Action config | Layout | Dim |
|---------------|--------|-----|
| `FrankaJointPositionActionCfg` | 7 arm joint targets + binary gripper | 8 |
| `FrankaIKActionCfg` | absolute EE pose `(x, y, z, qw, qx, qy, qz)` + binary gripper | 8 |
| `FrankaRelIKActionCfg` | relative EE pose `(dx, dy, dz, droll, dpitch, dyaw)` + binary gripper | 7 |

- **Config classes:** `FrankaCfg` (one per variant file; action configs in `franka_definitions.py`)
- **Proprioception:** EE frame pose and finger joint positions (`franka_definitions.py`)
- **Contact gripper:** `{"gripper": ...panda_leftfinger}`

```python
from robolab.robots.franka import FrankaCfg                      # standard PD
from robolab.robots.franka_high_pd import FrankaCfg              # high PD, gravity disabled
from robolab.robots.franka_definitions import FrankaJointPositionActionCfg, contact_gripper
```

---

Also in this folder: `delta_actions.py`, a helper that converts a target EE pose into a relative
(delta) pose action. It does not define an action space.

The robot stills above are rendered in an empty scene at each robot's reset posture.
