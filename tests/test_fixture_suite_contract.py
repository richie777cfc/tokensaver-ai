"""Contract tests for the fixture benchmark suite.

Runs the full benchmark suite against public fixtures and verifies:
- schema_version is present in suite outputs
- summary shape is stable
- per-result shape is stable
- public export is sanitized
- expected fixture benchmarks are present and not failed
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tokensaver import SCHEMA_VERSION
from tokensaver.benchmark import benchmark_suite

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_MANIFEST = REPO_ROOT / "benchmarks" / "fixtures" / "manifest.ci.json"

EXPECTED_BENCHMARK_IDS = {
    "flutter-fixture", "react-native-fixture", "python-fixture",
    "node-fixture", "nextjs-fixture", "fastapi-fixture",
    "django-fixture", "spring-boot-fixture", "go-fixture",
    "android-native-fixture", "ios-swift-fixture",
    "react-web-fixture", "angular-fixture",
}

SUITE_SUMMARY_REQUIRED_KEYS = {
    "benchmark_count",
    "success_count",
    "failed_count",
    "unsupported_count",
    "partial_count",
    "success_rate",
    "framework_detection_accuracy",
    "per_stack",
    "artifact_presence_rate",
    "empty_artifact_rate",
    "low_value_artifact_rate",
}

PER_RESULT_REQUIRED_KEYS = {
    "id",
    "label",
    "publish_label",
    "expected_framework",
    "tags",
    "private",
    "detected_framework",
    "plugin",
    "status",
    "failure_reason",
    "runtime_seconds",
    "scan",
    "repo",
    "artifacts",
}


class FixtureSuiteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = benchmark_suite(FIXTURE_MANIFEST, output_root=temp_dir)
            cls._suite = json.loads(Path(result["suite_path"]).read_text())
            cls._public = json.loads(Path(result["public_path"]).read_text())
            cls._markdown = Path(result["md_path"]).read_text()

    def test_suite_schema_version(self) -> None:
        self.assertEqual(self._suite["_meta"]["schema_version"], SCHEMA_VERSION)

    def test_public_schema_version(self) -> None:
        self.assertEqual(self._public["_meta"]["schema_version"], SCHEMA_VERSION)

    def test_suite_top_level_shape(self) -> None:
        for key in ("_meta", "suite", "summary", "results"):
            self.assertIn(key, self._suite)

    def test_summary_required_keys(self) -> None:
        summary = self._suite["summary"]
        for key in SUITE_SUMMARY_REQUIRED_KEYS:
            self.assertIn(key, summary, f"Summary missing key: {key}")

    def test_expected_benchmarks_present(self) -> None:
        result_ids = {r["id"] for r in self._suite["results"]}
        self.assertEqual(
            EXPECTED_BENCHMARK_IDS,
            result_ids,
            f"Unexpected benchmark set: {result_ids}",
        )

    def test_per_result_required_keys(self) -> None:
        for result in self._suite["results"]:
            for key in PER_RESULT_REQUIRED_KEYS:
                self.assertIn(
                    key,
                    result,
                    f"Result {result.get('id')} missing key: {key}",
                )

    def test_no_fixture_is_failed(self) -> None:
        for result in self._suite["results"]:
            self.assertNotEqual(
                result["status"],
                "failed",
                f"{result['id']} should not be failed",
            )

    def test_supported_fixtures_are_ok(self) -> None:
        by_id = {r["id"]: r for r in self._suite["results"]}
        supported_ids = [
            "flutter-fixture",
            "react-native-fixture",
            "python-fixture",
            "node-fixture",
            "nextjs-fixture",
            "fastapi-fixture",
            "django-fixture",
            "spring-boot-fixture",
            "go-fixture",
            "android-native-fixture",
            "ios-swift-fixture",
            "react-web-fixture",
            "angular-fixture",
        ]
        for fixture_id in supported_ids:
            self.assertEqual(
                by_id[fixture_id]["status"],
                "ok",
                f"{fixture_id} should have status 'ok', got '{by_id[fixture_id]['status']}'",
            )

    def test_framework_detection_accuracy_is_perfect(self) -> None:
        accuracy = self._suite["summary"]["framework_detection_accuracy"]
        self.assertEqual(accuracy, 1.0, "All fixtures should have correct framework detection")

    def test_public_export_no_local_paths(self) -> None:
        text = json.dumps(self._public)
        self.assertNotIn(str(Path.home()), text)
        self.assertNotIn("/tmp/", text)

    def test_public_result_count_matches(self) -> None:
        self.assertEqual(
            len(self._suite["results"]),
            len(self._public["results"]),
        )

    def test_markdown_has_overview(self) -> None:
        self.assertIn("Benchmark Results", self._markdown)

    def test_benchmark_count_matches(self) -> None:
        manifest = json.loads(FIXTURE_MANIFEST.read_text())
        expected_count = len(manifest["benchmarks"])
        self.assertEqual(self._suite["summary"]["benchmark_count"], expected_count)
        self.assertEqual(self._public["summary"]["benchmark_count"], expected_count)


if __name__ == "__main__":
    unittest.main()
