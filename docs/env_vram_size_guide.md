# 并行环境数与显存

当前内置范围为 [8 个任务、5 个场景](benchmark.md)。使用 `--num-envs` 设置并行环境数，`--num-runs` 设置每个任务的运行批次；固定批次数模式的 episode 数为两者乘积。

从单环境开始，检查模型与仿真的总显存占用后再增加并行环境数：

```bash
python policies/pi0_family/run.py --policy pi05 --task BananaInBowlTask --headless --num-envs 1
```

相机数量与分辨率、渲染模式、场景碰撞体、是否记录图像，以及模型是否与仿真共用 GPU，都会影响显存占用。可用 `nvidia-smi` 观察加载完成和实际推理时的占用。不要仅根据空场景或模型尚未加载时的占用设置并行数。

如需 20 个 episode，可按设备容量选择 4 个环境 × 5 批，或 1 个环境 × 20 批：

```bash
python policies/pi0_family/run.py --policy pi05 --task BananaInBowlTask --headless --num-envs 4 --num-runs 5
```

本仓库没有这 8 个任务在各型号 GPU 上的完整显存上限测量表。比较实验时保持 simulator、模型、相机、并行数与渲染配置一致；具体配置会记录在运行输出中。
