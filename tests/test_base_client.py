# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import numpy as np

from policyloop.eval.base_client import InferenceClient


class _Client(InferenceClient):
    def __init__(self):
        super().__init__()
        self.requests = []

    def _extract_observation(self, raw_obs, *, env_id=0):
        return raw_obs

    def _pack_request(self, extracted_obs, instruction):
        return {"prompt": instruction}

    def _query_server(self, request):
        self.requests.append(request)
        return {"actions": [[0.0]]}

    def _unpack_response(self, response):
        return np.asarray(response["actions"])


def test_base_client_wire_format_is_unchanged():
    client = _Client()
    client.begin_episode(7)

    client.infer({}, "task")

    assert client.requests[0] == {"prompt": "task"}


def test_begin_episode_is_part_of_the_core_contract():
    client = _Client()
    client.begin_episode(5)
    assert client._eval_episode_idx == 5

