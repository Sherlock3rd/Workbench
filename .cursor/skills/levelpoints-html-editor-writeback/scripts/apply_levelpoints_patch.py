#!/usr/bin/env python3
import argparse
import copy
import json
from pathlib import Path


DEFAULT_ALLOWED_MB_FIELDS = {
    "ObjID",
    "ObjType",
    "AreaID",
    "NpcID",
    "TeamID",
    "BelongToLayerID",
    "SubID",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def as_number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    return value


def component_identity(component):
    mb = ((component.get("serializedData") or {}).get("MonoBehaviour") or {})
    return {
        "subID": component.get("subID") or mb.get("SubID"),
        "className": component.get("className"),
        "prefabPath": component.get("prefabPath"),
    }


def assert_identity(edit, component, index):
    expected = edit.get("match") or {}
    if not expected:
        return
    actual = component_identity(component)
    for key, expected_value in expected.items():
        if expected_value is None:
            continue
        if actual.get(key) != expected_value:
            raise ValueError(
                f"edit for index {index} does not match {key}: "
                f"expected {expected_value!r}, found {actual.get(key)!r}"
            )


def apply_position(component, position, index):
    if not isinstance(position, dict):
        raise ValueError(f"edit for index {index} has invalid position")
    current = component.setdefault("position", {})
    for axis in ("x", "y", "z"):
        if axis in position:
            current[axis] = as_number(position[axis], f"position.{axis}")


def apply_mono_behaviour(component, values, index, allowed_fields):
    if not isinstance(values, dict):
        raise ValueError(f"edit for index {index} has invalid monoBehaviour")
    mb = component.setdefault("serializedData", {}).setdefault("MonoBehaviour", {})
    for field, value in values.items():
        if field not in allowed_fields:
            raise ValueError(f"edit for index {index} attempts unsupported MonoBehaviour field {field!r}")
        mb[field] = value


def normalize_edits(patch):
    if isinstance(patch, list):
        return patch
    if isinstance(patch, dict) and isinstance(patch.get("edits"), list):
        return patch["edits"]
    raise ValueError("patch must be a list or an object with an edits array")


def apply_patch(levelpoints, patch, allowed_fields):
    result = copy.deepcopy(levelpoints)
    components = result.get("components")
    if not isinstance(components, list):
        raise ValueError("LevelPoints JSON must contain a components array")

    changed = []
    for edit in normalize_edits(patch):
        if not isinstance(edit, dict):
            raise ValueError("each edit must be an object")
        if "index" not in edit:
            raise ValueError("each edit must include components[] index")
        index = edit["index"]
        if isinstance(index, bool) or not isinstance(index, int):
            raise ValueError(f"edit index must be an integer, got {index!r}")
        if index < 0 or index >= len(components):
            raise ValueError(f"edit index {index} is outside components length {len(components)}")

        component = components[index]
        assert_identity(edit, component, index)
        before = copy.deepcopy(component)
        if "position" in edit:
            apply_position(component, edit["position"], index)
        if "monoBehaviour" in edit:
            apply_mono_behaviour(component, edit["monoBehaviour"], index, allowed_fields)
        if before != component:
            changed.append(index)

    return result, changed


def main():
    parser = argparse.ArgumentParser(description="Apply HTML editor patches to Unity LevelPoints.json.")
    parser.add_argument("--levelpoints", required=True, help="Source Unity LevelEditor LevelPoints.json")
    parser.add_argument("--patch", required=True, help="Patch JSON exported by the HTML editor")
    parser.add_argument("--out", required=True, help="Output LevelPoints JSON for Unity to read")
    parser.add_argument(
        "--allow-field",
        action="append",
        default=[],
        help="Additional serializedData.MonoBehaviour field allowed for writeback",
    )
    parser.add_argument("--summary", help="Optional JSON summary output")
    args = parser.parse_args()

    levelpoints = load_json(args.levelpoints)
    patch = load_json(args.patch)
    allowed_fields = set(DEFAULT_ALLOWED_MB_FIELDS) | set(args.allow_field)
    updated, changed = apply_patch(levelpoints, patch, allowed_fields)
    write_json(args.out, updated)

    summary = {
        "source": str(args.levelpoints),
        "patch": str(args.patch),
        "output": str(args.out),
        "component_count": len(levelpoints.get("components") or []),
        "changed_count": len(changed),
        "changed_indices": changed,
    }
    if args.summary:
        write_json(args.summary, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
