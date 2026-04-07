from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tokensaver.benchmark import (
    benchmark_suite,
    compute_suite_summary,
    diff_snapshots,
    export_public_results,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_MANIFEST = REPO_ROOT / "benchmarks" / "fixtures" / "manifest.ci.json"


class BenchmarkContractTests(unittest.TestCase):
    def test_export_public_results_anonymizes_private_ids(self) -> None:
        payload = {
            "_meta": {
                "extractor": "benchmark_suite_v2",
                "generated_at": "2026-04-07T00:00:00+00:00",
                "manifest": "/Users/example/private.json",
            },
            "suite": "private-suite",
            "summary": {"benchmark_count": 1},
            "results": [
                {
                    "id": "secret-repo-id",
                    "label": "Secret Repo",
                    "publish_label": "Confidential App",
                    "private": True,
                    "detected_framework": "react_native",
                    "plugin": "react_native",
                    "status": "ok",
                    "failure_reason": None,
                    "runtime_seconds": 1.23,
                    "scan": {"total_files": 10, "total_tokens": 100},
                    "repo": {"compression_ratio": 5.0},
                    "artifacts": {},
                }
            ],
        }

        public_payload = export_public_results(payload)
        result = public_payload["results"][0]
        self.assertEqual(result["label"], "Confidential App")
        self.assertNotEqual(result["id"], "secret-repo-id")
        self.assertNotIn("manifest", public_payload["_meta"])

    def test_compute_suite_summary_counts_partial_empty_artifacts(self) -> None:
        summary = compute_suite_summary(
            [
                {
                    "status": "partial",
                    "expected_framework": "python",
                    "detected_framework": "python",
                    "runtime_seconds": 0.5,
                    "repo": {"compression_ratio": 2.0},
                    "artifacts": {
                        "module_graph": {"entity_count": 0, "compression_ratio": None},
                        "api_index": {"entity_count": 1, "compression_ratio": 2.5},
                    },
                }
            ]
        )

        self.assertEqual(summary["partial_count"], 1)
        self.assertEqual(summary["benchmark_count"], 1)
        self.assertEqual(summary["empty_artifact_rate"], 0.5)
        self.assertEqual(summary["framework_detection_accuracy"], 1.0)

    def test_diff_snapshots_reports_runtime_and_ratio_changes(self) -> None:
        old_payload = {
            "results": [
                {
                    "id": "fixture",
                    "label": "Fixture",
                    "publish_label": "Fixture",
                    "private": False,
                    "status": "ok",
                    "detected_framework": "flutter",
                    "runtime_seconds": 1.0,
                    "repo": {"compression_ratio": 2.0},
                    "artifacts": {"api_index": {"compression_ratio": 1.5}},
                }
            ]
        }
        new_payload = {
            "results": [
                {
                    "id": "fixture",
                    "label": "Fixture",
                    "publish_label": "Fixture",
                    "private": False,
                    "status": "ok",
                    "detected_framework": "flutter",
                    "runtime_seconds": 1.5,
                    "repo": {"compression_ratio": 3.0},
                    "artifacts": {"api_index": {"compression_ratio": 2.0}},
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            old_path = temp_root / "old.json"
            new_path = temp_root / "new.json"
            old_path.write_text(json.dumps(old_payload))
            new_path.write_text(json.dumps(new_payload))

            diff = diff_snapshots(old_path, new_path)

        self.assertEqual(diff["compression_ratio_delta"]["fixture"]["delta"], 1.0)
        self.assertEqual(diff["runtime_delta"]["fixture"]["delta"], 0.5)
        self.assertEqual(
            diff["artifact_ratio_deltas"]["fixture"]["api_index"]["delta"],
            0.5,
        )

    def test_benchmark_suite_fixture_outputs_public_safe_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = benchmark_suite(FIXTURE_MANIFEST, output_root=temp_dir)
            suite_json = json.loads(Path(result["suite_path"]).read_text())
            public_json = json.loads(Path(result["public_path"]).read_text())
            markdown = Path(result["md_path"]).read_text()

        self.assertEqual(suite_json["summary"]["benchmark_count"], 4)
        self.assertEqual(public_json["summary"]["benchmark_count"], 4)
        self.assertIn("Benchmark Results", markdown)
        public_text = json.dumps(public_json)
        self.assertNotIn(str(Path.home()), public_text)

    def test_benchmark_suite_public_only_omits_raw_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = benchmark_suite(FIXTURE_MANIFEST, output_root=temp_dir, public_only=True)
            output_root = Path(temp_dir)
            self.assertIsNone(result["suite_path"])
            self.assertIsNone(result["snapshot_path"])
            self.assertTrue((output_root / "SUITE_RESULTS.public.json").exists())
            self.assertTrue((output_root / "SUITE_RESULTS.md").exists())
            self.assertFalse((output_root / "SUITE_RESULTS.json").exists())
            self.assertFalse((output_root / "history").exists())
            self.assertEqual(list(output_root.glob("*/BENCHMARK.json")), [])


if __name__ == "__main__":
    unittest.main()
