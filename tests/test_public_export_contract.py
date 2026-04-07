"""Contract tests for public export sanitization.

Verifies that SUITE_RESULTS.public.json:
- carries schema_version
- has the same top-level shape as SUITE_RESULTS.json
- never contains local paths
- anonymizes private benchmark identifiers
- strips private manifest paths from _meta
"""

from __future__ import annotations

import json
import re
import unittest

from tokensaver import SCHEMA_VERSION
from tokensaver.benchmark import export_public_results

_PATH_PATTERNS = [
    re.compile(r"/Users/[^\s:\"]+"),
    re.compile(r"/home/[^\s:\"]+"),
    re.compile(r"[A-Za-z]:\\[^\s\"]+"),
]


def _make_suite_payload(
    *,
    private: bool = False,
    manifest_path: str = "/local/path/manifest.json",
    failure_reason: str | None = None,
) -> dict:
    return {
        "_meta": {
            "schema_version": SCHEMA_VERSION,
            "extractor": "benchmark_suite_v2",
            "generated_at": "2026-04-07T00:00:00+00:00",
            "manifest": manifest_path,
        },
        "suite": "test-suite",
        "summary": {
            "benchmark_count": 1,
            "success_count": 1,
            "failed_count": 0,
            "unsupported_count": 0,
            "partial_count": 0,
            "success_rate": 1.0,
            "framework_detection_accuracy": 1.0,
            "per_stack": {},
            "artifact_presence_rate": 1.0,
            "empty_artifact_rate": 0.0,
            "low_value_artifact_rate": 0.0,
        },
        "results": [
            {
                "id": "my-secret-repo",
                "label": "Secret Repo Label",
                "publish_label": "Public App Name",
                "expected_framework": "flutter",
                "tags": ["fixture"],
                "private": private,
                "detected_framework": "flutter",
                "plugin": "flutter",
                "status": "ok",
                "failure_reason": failure_reason,
                "runtime_seconds": 0.42,
                "scan": {"total_files": 10, "total_tokens": 500},
                "repo": {
                    "source_file_count": 5,
                    "union_source_tokens": 400,
                    "bundle_tokens": 100,
                    "compression_ratio": 4.0,
                    "overlap_source_tokens": 50,
                },
                "artifacts": {
                    "module_graph": {
                        "entity_count": 2,
                        "source_tokens": 200,
                        "output_tokens": 50,
                        "compression_ratio": 4.0,
                    }
                },
            }
        ],
    }


class PublicExportContractTests(unittest.TestCase):
    def test_public_export_top_level_shape(self) -> None:
        payload = _make_suite_payload()
        public = export_public_results(payload)
        for key in ("_meta", "suite", "summary", "results"):
            self.assertIn(key, public)
        self.assertIsInstance(public["results"], list)
        self.assertEqual(len(public["results"]), 1)

    def test_schema_version_preserved(self) -> None:
        payload = _make_suite_payload()
        public = export_public_results(payload)
        self.assertEqual(public["_meta"]["schema_version"], SCHEMA_VERSION)

    def test_private_manifest_stripped(self) -> None:
        payload = _make_suite_payload(manifest_path="/Users/dev/repos/manifest.json")
        public = export_public_results(payload)
        self.assertNotIn("manifest", public["_meta"])

    def test_relative_manifest_preserved(self) -> None:
        payload = _make_suite_payload(manifest_path="benchmarks/fixtures/manifest.ci.json")
        public = export_public_results(payload)
        self.assertEqual(public["_meta"]["manifest"], "benchmarks/fixtures/manifest.ci.json")

    def test_private_id_anonymized(self) -> None:
        payload = _make_suite_payload(private=True)
        public = export_public_results(payload)
        result = public["results"][0]
        self.assertNotEqual(result["id"], "my-secret-repo")
        self.assertEqual(result["label"], "Public App Name")

    def test_public_id_preserved(self) -> None:
        payload = _make_suite_payload(private=False)
        public = export_public_results(payload)
        result = public["results"][0]
        self.assertEqual(result["id"], "my-secret-repo")

    def test_failure_reason_sanitized(self) -> None:
        payload = _make_suite_payload(
            failure_reason="FileNotFoundError: /Users/dev/projects/secret/main.py"
        )
        public = export_public_results(payload)
        reason = public["results"][0]["failure_reason"]
        self.assertNotIn("/Users/dev", reason)
        self.assertIn("<redacted>", reason)

    def test_no_local_paths_in_public_output(self) -> None:
        payload = _make_suite_payload(
            private=True,
            manifest_path="/home/ci/workspace/manifest.json",
            failure_reason="Error in /Users/dev/src/main.dart",
        )
        public = export_public_results(payload)
        text = json.dumps(public)
        for pattern in _PATH_PATTERNS:
            matches = pattern.findall(text)
            self.assertEqual(
                matches,
                [],
                f"Local path found in public export: {matches}",
            )

    def test_per_result_required_fields(self) -> None:
        payload = _make_suite_payload()
        public = export_public_results(payload)
        result = public["results"][0]
        for key in (
            "id",
            "label",
            "detected_framework",
            "plugin",
            "status",
            "runtime_seconds",
            "scan",
            "repo",
            "artifacts",
        ):
            self.assertIn(key, result, f"Required field {key} missing from public result")

    def test_summary_shape_matches(self) -> None:
        payload = _make_suite_payload()
        public = export_public_results(payload)
        summary = public["summary"]
        for key in (
            "benchmark_count",
            "success_count",
            "failed_count",
            "success_rate",
        ):
            self.assertIn(key, summary, f"Required summary field {key} missing")


if __name__ == "__main__":
    unittest.main()
