"""Keep bundled files, default discovery, metadata and documentation in agreement."""

import argparse
import csv
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import unquote

import pytest

from policyloop.constants import DEFAULT_TASK_SUBFOLDERS, PACKAGE_DIR, SCENE_DIR, TASK_DIR
from policyloop.core.task.task_utils import find_task_files, load_task_from_file
from policyloop.core.utils.usd_utils import get_usd_objects_info
from policyloop.eval.runner import add_common_eval_args
from policyloop.tasks._utils.load_task_info import extract_task_metadata_from_file

ROOT = Path(PACKAGE_DIR)
TASK_SCENES = {
    "BananaInBowlTask": "banana_bowl.usda",
    "BananaThenRubiksCubeTask": "rubiks_cube_banana_bowl.usda",
    "BananasInBinThreeTotalTask": "bananas_5_grey_bin.usda",
    "BlockStackingOrderAgnosticTask": "colored_blocks.usda",
    "BlockStackingSpecifiedOrderTask": "colored_blocks.usda",
    "RubiksCubeAndBananaTask": "rubiks_cube_banana_bowl.usda",
    "RubiksCubeLeftOfBowlTask": "rubiks_cube_banana_bowl.usda",
    "RubiksCubeOrBananaTask": "rubiks_cube_banana_bowl.usda",
}
SCENES = set(TASK_SCENES.values()) | {"base_empty.usda"}


def _read_json(relative):
    return json.loads((ROOT / relative).read_text())


def test_task_sources_and_metadata_match():
    files = find_task_files(Path(TASK_DIR) / "benchmark")
    actual = {
        load_task_from_file(p, allow_multiple=False).__name__: p for p in files
    }
    metadata = _read_json("policyloop/tasks/_metadata/task_metadata.json")
    assert len(metadata) == len(TASK_SCENES)
    assert set(actual) == {row["task_name"] for row in metadata} == set(TASK_SCENES)
    for row in metadata:
        assert row["scene"] == TASK_SCENES[row["task_name"]]
        source = Path(TASK_DIR) / row["filename"]
        assert source.resolve() == Path(actual[row["task_name"]]).resolve()
        fresh = extract_task_metadata_from_file(str(source), TASK_DIR)
        assert row == fresh, row["task_name"]


def test_task_csv_and_readme_match():
    with (ROOT / "policyloop/tasks/_metadata/task_table.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(TASK_SCENES)
    assert {row["task_name"].split(" (")[0] for row in rows} == set(TASK_SCENES)
    for name in TASK_SCENES:
        assert name in (ROOT / "policyloop/tasks/README.md").read_text()
        assert name in (ROOT / "docs/benchmark.md").read_text()


def test_scene_inventory_and_metadata_match():
    actual = {p.name for p in Path(SCENE_DIR).iterdir()
              if p.suffix.lower() in {".usd", ".usda", ".usdc", ".usdz"}}
    metadata = _read_json("assets/scenes/_metadata/scene_metadata.json")
    assert actual == set(metadata) == SCENES
    for scene, records in metadata.items():
        fresh = get_usd_objects_info(str(Path(SCENE_DIR) / scene))
        assert records == json.loads(json.dumps(fresh))
        for record in records:
            assert type(record["rigid_body"]) is bool
            for payload in record["payload"]:
                assert (Path(SCENE_DIR) / payload).resolve().is_file(), payload
        assert (Path(SCENE_DIR) / "_images" / (Path(scene).stem + ".png")).is_file()
    with (Path(SCENE_DIR) / "_metadata/scene_table.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert {row["scene"] for row in rows} == SCENES


def _load_asset_tool(name):
    path = Path(SCENE_DIR) / "_utils" / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scene_statistics_include_the_template():
    metadata = _read_json("assets/scenes/_metadata/scene_metadata.json")
    stats = _read_json("assets/scenes/_metadata/scene_statistics.json")
    fresh = _load_asset_tool("compute_scene_statistics").compute_statistics(metadata)
    assert stats == json.loads(json.dumps(fresh))
    assert stats["total_scenes"] == 5
    assert set(stats["per_scene_object_counts"]) == SCENES


def test_table_map_matches_authored_payloads():
    mapping = _load_asset_tool("table_texture").SCENE_TABLE_TEXTURE_MAP
    assert set(mapping) == SCENES
    for scene, table in mapping.items():
        assert "@../fixtures/" + table + "@" in (Path(SCENE_DIR) / scene).read_text()
        assert (Path(SCENE_DIR).parent / "fixtures" / table).is_file()


def test_runner_defaults_to_bundled_tasks():
    parser = argparse.ArgumentParser()
    add_common_eval_args(parser)
    args = parser.parse_args([])
    assert args.task_dirs == DEFAULT_TASK_SUBFOLDERS == ["benchmark"]
    assert args.task is None
    assert args.tag is None


def _markdown_files():
    for folder in ("docs", "policies", "skills", "assets", "policyloop"):
        yield from (ROOT / folder).rglob("*.md")
    yield ROOT / "README.md"


def test_documentation_has_no_missing_local_links():
    broken = []
    for path in _markdown_files():
        text = path.read_text()
        targets = re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", text)
        targets += re.findall(r'(?:src|href)="([^"]+)"', text)
        for target in targets:
            target = unquote(target.split("#", 1)[0]).strip("<>")
            if not target or re.match(r"[a-z]+:", target) or target.startswith("//"):
                continue
            if not (path.parent / target).exists():
                broken.append((str(path.relative_to(ROOT)), target))
    assert not broken, broken


def test_documented_builtin_task_names_exist():
    for path in _markdown_files():
        text = path.read_text()
        declared_examples = set(re.findall(r"class\s+(\w+Task)\s*\(", text))
        names = set(re.findall(r"\b[A-Z][A-Za-z0-9_]+Task\b", text))
        assert names <= set(TASK_SCENES) | declared_examples | {"MyTask", "CustomTask"}, (
            str(path.relative_to(ROOT)), sorted(names - set(TASK_SCENES) - declared_examples)
        )
