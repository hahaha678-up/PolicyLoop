# Policy 自动化闭环评测

基于 Isaac Lab 的机器人 Policy 自动化闭环评测项目。当前内置 **8 个 Task、5 个 Scene**，围绕 Policy 接入、并行闭环执行、任务阶段判定和评测条件控制组织代码。

- **Policy 接入**：模型在独立服务端运行，客户端负责观测转换、推理通信和动作后处理。保留 Pi0 family 与 GR00T 两类客户端。
- **评测运行**：统一 runner 调用客户端，在多个环境中维护动作序列、独立终止状态和 episode 记录。
- **任务判定**：Conditional → Subtask → State Machine，记录阶段进度、条件状态和交互事件。
- **条件控制**：相机位置、背景、灯光和桌面材质变化；Scene Generation Skill 用于生成新的场景。

## 演示

https://github.com/user-attachments/assets/4b5084ed-6620-4d90-97b0-de6d4f437c15

视频依次展示四环境评测画面、任务阶段与阶段内进度，以及相机、光照、背景和桌面材质四类扰动。第一段选取真实成功的堆积木录像组合展示；第二段完整展示香蕉、魔方依次入碗的成功过程。视频采用连续倍速播放。

## 内置范围

| 内容 | 当前范围 |
|---|---|
| 任务 | 8 个，全部位于 [benchmark/](policyloop/tasks/benchmark/) |
| 场景 | 4 个评测场景 + `base_empty.usda` 场景生成模板 |
| 物体与背景 | 24 个物体 USD、4 个 HDR/EXR 背景 |
| 机器人配置 | DROID、Franka；DROID Joint Position / Abs IK / Rel IK |
| 默认评测入口 | Pi0.5 + DROID Joint Position；未传 `--task` 时遍历 8 个任务 |
| 可选客户端 | Pi0 family 其他变体、GR00T；服务端与权重需单独准备 |

[任务与场景对应表](docs/benchmark.md) · [任务 metadata](policyloop/tasks/README.md) · [场景索引](assets/scenes/README.md) · [物体索引](assets/objects/README.md)

## 代码入口

```text
policies/pi0_family/      Pi0 family 客户端和评测/扰动入口
policies/gr00t/           GR00T 客户端和评测入口
policyloop/eval/          共享 runner、episode 循环
policyloop/registrations/ 任务、机器人、观测与控制配置的组合注册
policyloop/core/task/     条件、子任务状态机、事件判定
policyloop/core/logging/  轨迹与结果记录
policyloop/tasks/         8 个内置任务及其 metadata
policyloop/variations/    相机、背景和光照配置
assets/                   场景、物体、机器人和材质资源
analysis/                 结果统计与检查
skills/                   Scene Generation Skill
tests/                    边界一致性与运行回归检查
```

## 环境与安装

仿真资产使用 Git LFS 保存。克隆仓库前请准备 Git LFS，克隆后在仓库根目录执行 `git lfs pull`，确认 USD、贴图和背景已下载。

运行环境：Linux、Python 3.11、Isaac Sim 5.0 / Isaac Lab 2.2、NVIDIA GPU。模型服务端使用独立环境。

```bash
# 在仓库根目录执行；需要已安装 uv 和系统 ffmpeg
uv sync --extra isaac50 --extra test
source .venv/bin/activate
export OMNI_KIT_ACCEPT_EULA=Y
```

默认 DROID 评测使用仓库内的本地仿真资产。模型权重需单独准备；显存需求见[并行环境数说明](docs/env_vram_size_guide.md)。

## 运行 Pi0.5

先按照 [Pi0 family 服务端说明](policies/pi0_family/README.md) 启动 OpenPI，并提供本地 checkpoint。服务端就绪后，在仓库根目录执行：

```bash
# 单任务闭环；服务端默认 localhost:8000
python policies/pi0_family/run.py --policy pi05 --task BananaInBowlTask --headless --num-envs 1 --num-runs 1

# 全部 8 个任务，每个任务 4 个并行环境
python policies/pi0_family/run.py --policy pi05 --headless --num-envs 4 --num-runs 1
```

输出写入 `output/<时间戳>_pi05/`。使用 [结果分析工具](docs/analysis.md) 查看成功率、子任务得分和事件记录。闭环正常结束与任务成功分别判断；任务结果以 episode 记录为准。

扰动入口默认选择两个代表任务，可用 `--task` 指定其余保留任务；背景矩阵组合这两个任务与 4 个背景。各入口见 [Pi0 family](policies/pi0_family/README.md#variation-scripts)。

## 验证

```bash
# 默认注册、runner 参数、任务/场景/metadata/文档的一致性
python -m pytest tests/test_repository_boundary.py tests/test_task_discovery_defaults.py tests/test_registered_envs.py tests/test_tasks_valid.py tests/test_runner_args.py -v

# 5 个场景和 8 个任务的 create/reset/step/render
python -m pytest tests/test_runtime_boundary.py -v

# 全部测试（需要 Isaac Sim 和 GPU）
python -m pytest tests/ -v
```

## 文档

[文档索引](docs/README.md) · [注册与配置](docs/environment_registration.md) · [统一评测](docs/environment_run.md) · [任务判定](docs/subtask.md) · [场景生成](skills/policyloop-scenegen/SKILL.md)
