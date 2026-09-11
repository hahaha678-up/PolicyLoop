# 内置任务与场景

默认任务目录为 `policyloop/tasks/benchmark/`，包含下列 8 个任务。任务类绑定指令、场景、终止条件与子任务状态机；多个任务可以复用同一个场景。

| Task | Scene | Time limit (s) | Subtasks | Difficulty |
|---|---|---:|---:|---|
| [BananaInBowlTask](../policyloop/tasks/benchmark/banana_in_bowl_task.py) | `banana_bowl.usda` | 50 | 1 | simple |
| [BananasInBinThreeTotalTask](../policyloop/tasks/benchmark/bananas_in_bin_three.py) | `bananas_5_grey_bin.usda` | 60 | 1 | moderate |
| [BananaThenRubiksCubeTask](../policyloop/tasks/benchmark/banana_then_rubiks_cube.py) | `rubiks_cube_banana_bowl.usda` | 60 | 2 | simple |
| [BlockStackingOrderAgnosticTask](../policyloop/tasks/benchmark/block_stacking_order_agnostic_task.py) | `colored_blocks.usda` | 90 | 3 | complex |
| [BlockStackingSpecifiedOrderTask](../policyloop/tasks/benchmark/block_stacking_specified_order_task.py) | `colored_blocks.usda` | 90 | 3 | complex |
| [RubiksCubeAndBananaTask](../policyloop/tasks/benchmark/rubiks_cube_and_banana_task.py) | `rubiks_cube_banana_bowl.usda` | 60 | 2 | simple |
| [RubiksCubeLeftOfBowlTask](../policyloop/tasks/benchmark/rubiks_cube_left_of_bowl.py) | `rubiks_cube_banana_bowl.usda` | 30 | 3 | moderate |
| [RubiksCubeOrBananaTask](../policyloop/tasks/benchmark/rubiks_cube_or_banana_task.py) | `rubiks_cube_banana_bowl.usda` | 30 | 1 | simple |

场景目录共 5 个 USD：上表引用的 4 个评测场景，以及 `base_empty.usda` 场景生成模板。模板没有对应的评测任务，不会由默认 runner 注册。

难度由当前任务的子任务数及技能权重计算：4 个 simple、2 个 moderate、2 个 complex。它描述任务结构，不是模型成功率。细节见 [子任务判定](subtask.md)。

## 默认注册与扩展

- Pi0 family 与 GR00T 的标准 runner 默认扫描 `benchmark`，支持这 8 个基础任务。
- DROID 提供 Joint Position、Abs IK、Rel IK 注册；Franka 的配置注册入口也组合这 8 个任务。
- 相机、灯光、背景和桌面变化是同一基础任务的评测条件，不增加基础任务数量。背景矩阵默认选取 BananaInBowlTask 与 RubiksCubeAndBananaTask，支持显式传入其他保留任务。
- [Scene Generation Skill](../skills/policyloop-scenegen/SKILL.md) 使用保留的物体库和模板。自定义场景/任务应按 [任务编写流程](task.md) 创建并显式指定路径；不包含在默认 8-task 范围中。

## 索引与验证

[任务 metadata](../policyloop/tasks/_metadata/task_metadata.json)、[CSV](../policyloop/tasks/_metadata/task_table.csv) 和 [任务表](../policyloop/tasks/README.md) 对应当前任务定义。[场景 metadata](../assets/scenes/_metadata/scene_metadata.json) 与 [场景表](../assets/scenes/README.md) 覆盖全部 5 个场景，包括模板。

```bash
python -m pytest tests/test_repository_boundary.py tests/test_registered_envs.py tests/test_tasks_valid.py -v
python -m pytest tests/test_runtime_boundary.py -v
```

第一组核对定义、注册、runner 默认值与索引；第二组使用 DROID Joint Position，对 5 个场景、8 个任务分别执行 create/reset/step/render，并检查任务状态机和事件接口。两组都不需要模型服务端。Policy 闭环由 [Pi0.5 入口](../policies/pi0_family/README.md) 单独执行，模型的任务成功率从运行输出统计。
