#!/usr/bin/env python3
"""Validate a feature-loop checkpoint and suggest compatible ready stages.

Read-only and standard-library only. References are checked for presence, not
truth: the coordinator must inspect code, evidence, and live worker state.
"""

import argparse
import json
from pathlib import Path
import re
import sys


ACTIVE = {"running", "review", "integrating"}
STATUSES = ACTIVE | {"pending", "done", "blocked"}
ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def string_list(value, label, allow_empty=True):
    require(isinstance(value, list), f"{label} must be a list")
    require(all(nonempty(item) for item in value), f"{label} must contain strings")
    require(len(value) == len(set(value)), f"{label} contains duplicates")
    require(allow_empty or bool(value), f"{label} must not be empty")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_checkpoint(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    if not text.lstrip().startswith("{"):
        blocks = re.findall(
            r"^```feature-loop[ \t]*\r?\n(.*?)^```[ \t]*\r?$",
            text,
            re.MULTILINE | re.DOTALL,
        )
        require(len(blocks) == 1, "expected exactly one feature-loop JSON fence")
        text = blocks[0]
    return json.loads(text, object_pairs_hook=unique_object)


def validate_scope(scope, label):
    if scope == ".":
        return
    require(
        not scope.startswith("/")
        and not any(char in scope for char in "\\*?[]:")
        and not any(char.isspace() and char != " " for char in scope),
        f"{label}: use a relative file or directory, without globs: {scope!r}",
    )
    parts = scope.removesuffix("/").split("/")
    require(
        all(part not in {"", ".", ".."} for part in parts),
        f"{label}: path must be normalized: {scope!r}",
    )


def scopes_overlap(left, right):
    if "." in (left, right):
        return True
    if left.rstrip("/") == right.rstrip("/"):
        return True
    return (left.endswith("/") and right.startswith(left)) or (
        right.endswith("/") and left.startswith(right)
    )


def conflicts(left, right):
    return any(
        scopes_overlap(a, b) for a in left["writes"] for b in right["writes"]
    ) or bool(set(left["resources"]) & set(right["resources"]))


def validate(data):
    require(isinstance(data, dict), "checkpoint must be an object")
    require(type(data.get("version")) is int and data["version"] == 1, "version must be 1")
    limit = data.get("max_active_stages")
    require(type(limit) is int and limit > 0, "max_active_stages must be a positive integer")
    stages = data.get("stages")
    require(isinstance(stages, list) and bool(stages), "stages must be a nonempty list")
    by_id = {}
    for stage in stages:
        require(isinstance(stage, dict), "each stage must be an object")
        stage_id = stage.get("id")
        require(
            isinstance(stage_id, str) and ID_PATTERN.fullmatch(stage_id),
            "stage id must contain letters, digits, dots, underscores, or hyphens",
        )
        require(stage_id not in by_id, f"duplicate stage id: {stage_id}")
        by_id[stage_id] = stage
        require(nonempty(stage.get("stage")), f"{stage_id}: missing stage document reference")
        require(
            isinstance(stage.get("status"), str) and stage["status"] in STATUSES,
            f"{stage_id}: unknown status",
        )
        require(type(stage.get("ready")) is bool, f"{stage_id}: ready must be a boolean")
        for field in ("depends_on", "writes", "resources"):
            string_list(stage.get(field), f"{stage_id}.{field}")
        for scope in stage["writes"]:
            validate_scope(scope, f"{stage_id}.writes")
        if stage["status"] in ACTIVE | {"done"}:
            require(stage["ready"], f"{stage_id}: {stage['status']} stage is not ready")
        if stage["status"] in ACTIVE:
            assignment = stage.get("assignment")
            require(isinstance(assignment, dict), f"{stage_id}: missing assignment")
            for field in ("owner", "workspace", "base_ref"):
                require(nonempty(assignment.get(field)), f"{stage_id}: missing assignment.{field}")
            require(Path(assignment["workspace"]).is_absolute(), f"{stage_id}: workspace must be absolute")
        if stage["status"] == "done":
            result = stage.get("result")
            require(isinstance(result, dict), f"{stage_id}: done without result")
            for field in ("change_ref", "review_ref", "integration_ref"):
                require(nonempty(result.get(field)), f"{stage_id}: done without result.{field}")
            string_list(result.get("evidence"), f"{stage_id}.result.evidence", allow_empty=False)
        if stage["status"] == "blocked":
            require(nonempty(stage.get("blocker")), f"{stage_id}: blocked without a reason")

    for stage in stages:
        for dependency in stage["depends_on"]:
            require(dependency in by_id, f"{stage['id']}: unknown dependency {dependency}")

    # Iterative cycle detection keeps large maps independent of Python's recursion limit.
    remaining = {stage["id"]: set(stage["depends_on"]) for stage in stages}
    while remaining:
        roots = {stage_id for stage_id, deps in remaining.items() if not deps}
        require(bool(roots), "dependency cycle involving: " + ", ".join(remaining))
        remaining = {stage_id: deps - roots for stage_id, deps in remaining.items() if stage_id not in roots}

    for stage in stages:
        if stage["status"] in ACTIVE | {"done"}:
            for dependency in stage["depends_on"]:
                require(
                    by_id[dependency]["status"] == "done",
                    f"{stage['id']}: {stage['status']} with unfinished dependency {dependency}",
                )

    active = [stage for stage in stages if stage["status"] in ACTIVE]
    require(len(active) <= limit, "active stages exceed max_active_stages")
    for index, left in enumerate(active):
        for right in active[index + 1:]:
            label = f"{left['id']} and {right['id']}"
            require(not conflicts(left, right), f"active stages conflict: {label}")
            require(
                left["assignment"]["owner"] != right["assignment"]["owner"],
                f"active stages share a worker: {label}",
            )
            require(
                Path(left["assignment"]["workspace"]).resolve()
                != Path(right["assignment"]["workspace"]).resolve(),
                f"active stages share a workspace: {label}",
            )
    return by_id, active


def inspect(data):
    by_id, active = validate(data)
    selected = []
    eligible = []
    waiting = {}
    for stage in data["stages"]:
        stage_id = stage["id"]
        if stage["status"] == "blocked":
            waiting[stage_id] = "blocked: " + stage["blocker"]
            continue
        if stage["status"] != "pending":
            continue
        deps = [dep for dep in stage["depends_on"] if by_id[dep]["status"] != "done"]
        if deps:
            waiting[stage_id] = "unfinished dependencies: " + ", ".join(deps)
        elif not stage["ready"]:
            waiting[stage_id] = "needs planning or readiness check"
        else:
            eligible.append(stage_id)
            occupied = active + selected
            overlaps = [other["id"] for other in occupied if conflicts(stage, other)]
            if overlaps:
                waiting[stage_id] = "scope/resource conflict with: " + ", ".join(overlaps)
            elif len(occupied) >= data["max_active_stages"]:
                waiting[stage_id] = "active-stage capacity reached"
            else:
                selected.append(stage)
    return {
        "active": [stage["id"] for stage in active],
        "eligible": eligible,
        "selected": [stage["id"] for stage in selected],
        "waiting": waiting,
        "all_done": all(stage["status"] == "done" for stage in data["stages"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path, help="specification with a feature-loop fence, or JSON")
    args = parser.parse_args()
    try:
        result = inspect(read_checkpoint(args.checkpoint))
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
