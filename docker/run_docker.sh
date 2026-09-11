#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

POLICYLOOP_DIR=$( cd $( dirname ${BASH_SOURCE[0]} )/.. && pwd )

IMAGE_NAME="${POLICYLOOP_REGISTRY:-policyloop}"
IMAGE_TAG="${1:-$(git rev-parse --short HEAD)}"

xhost +local:root
docker run \
  -it \
  --entrypoint /bin/bash \
  -e DISPLAY \
  --net host \
  --rm \
  --runtime nvidia \
  -v $POLICYLOOP_DIR/.cache/ov:/root/.cache/ov \
  -v $POLICYLOOP_DIR/.cache/kit:/isaac-sim/kit/cache \
  -v $POLICYLOOP_DIR:/workspace/policyloop \
  -w /workspace/policyloop \
  "${IMAGE_NAME}:${IMAGE_TAG}"
xhost -local:root
