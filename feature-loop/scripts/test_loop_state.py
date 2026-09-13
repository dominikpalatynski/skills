"""Behavioral checks for checkpoint validation and scheduling decisions."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import loop_state


def stage(stage_id, **overrides):
    value = {
        "id": stage_id,
        "stage": f"{stage_id}.md",
        "depends_on": [],
        "status": "pending",
        "ready": True,
        "writes": [f"src/{stage_id}/"],
        "resources": [],
    }
    value.update(overrides)
    return value


def checkpoint(*stages, limit=2):
    return {"version": 1, "max_active_stages": limit, "stages": list(stages)}


def completed(stage_id, **overrides):
    return stage(
        stage_id,
        status="done",
        result={
            "change_ref": "commit:implementation",
            "evidence": [f"{stage_id}.md#verification"],
            "review_ref": f"{stage_id}.md#review",
            "integration_ref": f"{stage_id}.md#combined-code-checks",
        },
        **overrides,
    )


def active(stage_id, **overrides):
    status = overrides.pop("status", "running")
    return stage(
        stage_id,
        status=status,
        assignment={
            "owner": f"worker-{stage_id}",
            "workspace": str(Path(tempfile.gettempdir()) / f"loop-test-{stage_id}"),
            "base_ref": "commit:integration-base",
        },
        **overrides,
    )


class SchedulingTests(unittest.TestCase):
    def test_dependencies_unlock_only_after_integration(self):
        data = checkpoint(
            active("P01", status="review"),
            stage("P02", depends_on=["P01"]),
            stage("P03", depends_on=["P01"]),
        )
        self.assertEqual(loop_state.inspect(data)["selected"], [])
        data["stages"][0] = completed("P01")
        self.assertEqual(loop_state.inspect(data)["selected"], ["P02", "P03"])

    def test_outlines_need_planning(self):
        result = loop_state.inspect(checkpoint(stage("P01", ready=False), stage("P02")))
        self.assertEqual(result["eligible"], ["P02"])
        self.assertIn("planning", result["waiting"]["P01"])

    def test_overlapping_directories_serialize_but_siblings_can_run(self):
        result = loop_state.inspect(checkpoint(
            stage("P01", writes=["src/export/"]),
            stage("P02", writes=["src/export/csv.ts"]),
            stage("P03", writes=["src/exporter/json.ts"]),
        ))
        self.assertEqual(result["selected"], ["P01", "P03"])
        self.assertIn("P01", result["waiting"]["P02"])

    def test_file_and_resource_collisions(self):
        for kwargs in ({"writes": ["src/shared.ts"]}, {"resources": ["db:test"]}):
            with self.subTest(kwargs=kwargs):
                result = loop_state.inspect(checkpoint(stage("P01", **kwargs), stage("P02", **kwargs)))
                self.assertEqual(result["selected"], ["P01"])

    def test_review_and_integration_hold_scopes_and_slots(self):
        for status in ("running", "review", "integrating"):
            with self.subTest(status=status):
                result = loop_state.inspect(checkpoint(
                    active("P01", status=status),
                    stage("P02", writes=["src/P01/file.py"]),
                    stage("P03"), stage("P04"),
                ))
                self.assertEqual(result["active"], ["P01"])
                self.assertEqual(result["selected"], ["P03"])

    def test_blocker_preserves_unrelated_progress(self):
        result = loop_state.inspect(checkpoint(
            stage("P01", status="blocked", blocker="External service unavailable"),
            stage("P02", depends_on=["P01"]),
            stage("P03"),
        ))
        self.assertEqual(result["selected"], ["P03"])
        self.assertFalse(result["all_done"])

    def test_root_scope_and_read_only_task(self):
        result = loop_state.inspect(checkpoint(
            stage("P01", writes=["."]), stage("P02"), stage("P03", writes=[]),
        ))
        self.assertEqual(result["selected"], ["P01", "P03"])

    def test_completed_records_and_final_repair(self):
        data = checkpoint(completed("P01"), completed("P02", depends_on=["P01"]))
        self.assertTrue(loop_state.inspect(data)["all_done"])
        data["stages"].append(stage("P03", depends_on=["P02"]))
        result = loop_state.inspect(data)
        self.assertFalse(result["all_done"])
        self.assertEqual(result["selected"], ["P03"])

    def test_inspection_does_not_mutate_checkpoint(self):
        data = checkpoint(active("P01"), stage("P02"))
        before = copy.deepcopy(data)
        loop_state.inspect(data)
        self.assertEqual(data, before)

    def test_invalidated_dependency_chain_requires_revalidation(self):
        data = checkpoint(
            completed("P01"), active("P02", depends_on=["P01"]),
            stage("P03", depends_on=["P02"]), stage("P04"),
        )
        data["stages"][0]["ready"] = False
        with self.assertRaises(ValueError):
            loop_state.inspect(data)
        # Once the coordinator has stopped affected workers, invalidate the set.
        for item in data["stages"][:3]:
            item["status"] = "pending"
            item["ready"] = False
            item.pop("result", None)
        self.assertEqual(loop_state.inspect(data)["selected"], ["P04"])
        # Fresh evidence for the prerequisite unlocks its ready dependent again.
        data["stages"][0] = completed("P01")
        data["stages"][1]["ready"] = True
        self.assertEqual(loop_state.inspect(data)["selected"], ["P02", "P04"])


class ValidationTests(unittest.TestCase):
    def test_invalid_graphs(self):
        cases = [
            checkpoint(stage("P01"), stage("P01")),
            checkpoint(stage("P01", depends_on=["missing"])),
            checkpoint(stage("P01", depends_on=["P01"])),
            checkpoint(stage("P01", depends_on=["P02"]), stage("P02", depends_on=["P01"])),
        ]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                loop_state.inspect(data)

    def test_active_collisions_and_duplicate_assignments(self):
        duplicate_workspace = active("P02")
        duplicate_workspace["assignment"]["workspace"] = active("P01")["assignment"]["workspace"]
        duplicate_owner = active("P02")
        duplicate_owner["assignment"]["owner"] = active("P01")["assignment"]["owner"]
        cases = [
            checkpoint(active("P01"), active("P02", writes=["src/P01/file.py"])),
            checkpoint(active("P01", resources=["db"]), active("P02", resources=["db"])),
            checkpoint(active("P01"), active("P02"), limit=1),
            checkpoint(active("P01"), duplicate_workspace),
            checkpoint(active("P01"), duplicate_owner),
        ]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                loop_state.inspect(data)

    def test_active_and_done_dependencies_must_be_done(self):
        for second in (active("P02", depends_on=["P01"]), completed("P02", depends_on=["P01"])):
            with self.subTest(second=second), self.assertRaises(ValueError):
                loop_state.inspect(checkpoint(stage("P01"), second))

    def test_evidence_review_and_integration_are_required(self):
        for field in ("change_ref", "evidence", "review_ref", "integration_ref"):
            done = completed("P01")
            del done["result"][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                loop_state.inspect(checkpoint(done))
        done = completed("P01")
        done["result"]["evidence"] = []
        with self.assertRaises(ValueError):
            loop_state.inspect(checkpoint(done))

    def test_invalid_types_statuses_and_scopes(self):
        invalid_stages = [
            stage("P01", status="finished"), stage("P01", ready="yes"),
            stage("P01", status="running"), stage("P01", status="blocked"),
            stage("P01", depends_on=[[]]), stage("P01", resources=["db", "db"]),
        ]
        for scope in ("/absolute", "../escape", "src/../escape", "src//file", "src/*.ts", "C:\\file"):
            invalid_stages.append(stage("P01", writes=[scope]))
        for value in invalid_stages:
            with self.subTest(value=value), self.assertRaises(ValueError):
                loop_state.inspect(checkpoint(value))
        for data in (checkpoint(), checkpoint(stage("P01"), limit=True), {"version": True}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                loop_state.inspect(data)


class CommandTests(unittest.TestCase):
    def run_cli(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.md"
            path.write_text(content, encoding="utf-8")
            command = [sys.executable, str(Path(loop_state.__file__).resolve()), str(path)]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(path.read_text(encoding="utf-8"), content)
            self.assertEqual([entry.name for entry in Path(directory).iterdir()], ["spec.md"])
            return result

    def test_plain_json_and_embedded_checkpoint(self):
        data = json.dumps(checkpoint(stage("P01"), stage("P02")))
        for content in (data, "# Contract\n\n```feature-loop\n" + data + "\n```\n\nExisting prose.\n"):
            with self.subTest(content=content):
                result = self.run_cli(content)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["selected"], ["P01", "P02"])

    def test_malformed_or_ambiguous_checkpoint_fails_without_selection(self):
        block = "```feature-loop\n" + json.dumps(checkpoint(stage("P01"))) + "\n```\n"
        for content in ("# No checkpoint", "{bad json}", '{"version": 1, "version": 2}', block + block):
            with self.subTest(content=content):
                result = self.run_cli(content)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("error", json.loads(result.stderr))


if __name__ == "__main__":
    unittest.main()
