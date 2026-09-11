# GR00T N1.7

This repository retains the GR00T client and runner for the eight bundled tasks. A GR00T server and checkpoint must be prepared separately; GR00T inference is not part of the current local validation.

[**GR00T N1.7**](https://github.com/NVIDIA/Isaac-GR00T) is NVIDIA's open vision-language-action model for generalized robot skills. This directory provides the PolicyLoop client for evaluating the [**GR00T N1.7 DROID checkpoint**](https://huggingface.co/nvidia/GR00T-N1.7-DROID) zero-shot on PolicyLoop tasks.

[`client.py`](./client.py) provides the `GR00TDroidJointposClient` class, which connects to the GR00T policy server over ZMQ. It converts PolicyLoop observations to the N1.7 DROID observation contract and returns joint-position and gripper action chunks. [`run.py`](./run.py) exposes the client through PolicyLoop's standard evaluation runner.

For the validated configuration, full benchmark results, observation contract, image-handling notes, multi-GPU layout, and troubleshooting guidance, see the [GR00T N1.7 DROID integration guide](https://github.com/NVIDIA/Isaac-GR00T/tree/main/examples/RoboLab).

Below is a quickstart for bringing up one GR00T policy server and running a PolicyLoop evaluation client.

## Server

Clone Isaac-GR00T with its submodules:

```shell
git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T.git
cd Isaac-GR00T
```

Follow the official [environment setup instructions](https://github.com/NVIDIA/Isaac-GR00T#set-up-the-environment). GR00T N1.7 also requires access to the gated [`nvidia/Cosmos-Reason2-2B`](https://huggingface.co/nvidia/Cosmos-Reason2-2B) backbone. After access is approved, authenticate without placing a token in this README or a launch command:

```shell
uv run hf auth login
```

Start the policy server with the DROID checkpoint and its matching embodiment tag:

```shell
CUDA_VISIBLE_DEVICES=0 uv run python gr00t/eval/run_gr00t_server.py \
  --model-path nvidia/GR00T-N1.7-DROID \
  --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT \
  --device cuda \
  --host 127.0.0.1 \
  --port 5555 \
  --use-sim-policy-wrapper
```

The server is ready when it reports that it is listening on `tcp://127.0.0.1:5555`.

## Client

Clone PolicyLoop and install its native environment. `uv sync` installs PolicyLoop's Isaac Sim, Isaac Lab, and GR00T client dependencies:

```shell
git clone https://github.com/hahaha678-up/PolicyLoop.git
cd PolicyLoop
sudo apt install ffmpeg
uv venv --python 3.11
source .venv/bin/activate
uv sync
export OMNI_KIT_ACCEPT_EULA=Y
```

Docker is optional. If you prefer an isolated, prebuilt Isaac Lab environment, follow PolicyLoop's [Docker guide](../../docker/README.md) instead.

Run a smoke test against the server. `--open-loop-horizon 8` is part of the validated N1.7 baseline and controls how many actions PolicyLoop executes from each predicted chunk before querying the server again:

```shell
uv run python policies/gr00t/run.py \
  --task BananaInBowlTask \
  --remote-host 127.0.0.1 \
  --remote-port 5555 \
  --open-loop-horizon 8
```

To evaluate multiple sub-environments in parallel in headless mode:

```shell
uv run python policies/gr00t/run.py \
  --task BananaInBowlTask \
  --remote-host 127.0.0.1 \
  --remote-port 5555 \
  --open-loop-horizon 8 \
  --num-envs 10 \
  --headless \
  --video-mode none
```

If the policy server runs on another host, bind it to the appropriate private interface, pass its reachable hostname to the client's `--remote-host`, and ensure TCP port `5555` is reachable only across the intended network boundary.

## Validated Client Settings

- Checkpoint: `nvidia/GR00T-N1.7-DROID`
- Embodiment tag: `OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT`
- Cameras: left exterior and left wrist
- Image transport: HWC `uint8` at `180x320`, with no letterboxing or black padding
- PolicyLoop execution horizon: `8`

These settings reproduce the documented PolicyLoop baseline. Treat changes to the image transform, camera set, or execution horizon as ablations rather than interchangeable defaults.
