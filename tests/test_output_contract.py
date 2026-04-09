"""Contract tests that lock the canonical output shape of build artifacts.

These tests verify:
- schema_version is present and correct in every artifact
- required top-level keys exist in every artifact
- field types match expectations
- no regression in the documented output contract
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tokensaver import SCHEMA_VERSION
from tokensaver.build import build_project

REPO_ROOT = Path(__file__).resolve().parents[1]
FLUTTER_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "flutter_fixture"
RN_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "react_native_fixture"
PYTHON_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "python_fixture"
NODE_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "node_fixture"
NEXTJS_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "nextjs_fixture"
PHP_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "php_fixture"
WORKSPACE_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "nextjs_python_web_workspace_fixture"

BUILD_ARTIFACT_FILES = {
    "PROJECT_SUMMARY.json",
    "COMMANDS.json",
    "MODULE_GRAPH.json",
    "API_INDEX.json",
    "ROUTE_INDEX.json",
    "CONFIG_INDEX.json",
    "METRICS.json",
}


class BuildOutputContractTests(unittest.TestCase):
    """Verify that build artifacts conform to the stable contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._results: dict[str, dict[str, dict]] = {}
        for name, fixture_path in [
            ("flutter", FLUTTER_FIXTURE),
            ("react_native", RN_FIXTURE),
            ("python", PYTHON_FIXTURE),
            ("node", NODE_FIXTURE),
            ("nextjs", NEXTJS_FIXTURE),
            ("php", PHP_FIXTURE),
            ("workspace", WORKSPACE_FIXTURE),
        ]:
            with tempfile.TemporaryDirectory() as temp_dir:
                build_project(fixture_path, output_dir=temp_dir)
                artifacts = {}
                for artifact_file in BUILD_ARTIFACT_FILES:
                    artifact_path = Path(temp_dir) / artifact_file
                    if artifact_path.exists():
                        artifacts[artifact_file] = json.loads(artifact_path.read_text())
                cls._results[name] = artifacts

    def test_all_artifacts_present(self) -> None:
        for fixture_name, artifacts in self._results.items():
            for artifact_file in BUILD_ARTIFACT_FILES:
                self.assertIn(
                    artifact_file,
                    artifacts,
                    f"{artifact_file} missing for {fixture_name}",
                )

    def test_schema_version_present_and_correct(self) -> None:
        for fixture_name, artifacts in self._results.items():
            for artifact_file, payload in artifacts.items():
                meta = payload.get("_meta", {})
                self.assertIn(
                    "schema_version",
                    meta,
                    f"schema_version missing in _meta of {artifact_file} ({fixture_name})",
                )
                self.assertEqual(
                    meta["schema_version"],
                    SCHEMA_VERSION,
                    f"schema_version mismatch in {artifact_file} ({fixture_name})",
                )

    def test_meta_has_required_fields(self) -> None:
        for fixture_name, artifacts in self._results.items():
            for artifact_file, payload in artifacts.items():
                meta = payload.get("_meta", {})
                self.assertIn("extractor", meta, f"extractor missing in {artifact_file} ({fixture_name})")
                self.assertIsInstance(meta["extractor"], str)

    def test_project_summary_shape(self) -> None:
        for fixture_name, artifacts in self._results.items():
            payload = artifacts["PROJECT_SUMMARY.json"]
            for key in ("_meta", "project_name", "framework", "tokenizer", "languages", "entrypoints", "manifests"):
                self.assertIn(key, payload, f"{key} missing in PROJECT_SUMMARY ({fixture_name})")
            self.assertIsInstance(payload["languages"], list)
            self.assertIsInstance(payload["entrypoints"], list)
            self.assertIsInstance(payload["manifests"], list)

    def test_commands_shape(self) -> None:
        for fixture_name, artifacts in self._results.items():
            payload = artifacts["COMMANDS.json"]
            self.assertIn("_meta", payload)
            self.assertIn("commands", payload)
            self.assertIsInstance(payload["commands"], list)

    def test_module_graph_shape(self) -> None:
        for fixture_name, artifacts in self._results.items():
            payload = artifacts["MODULE_GRAPH.json"]
            self.assertIn("_meta", payload)
            self.assertIn("modules", payload)
            self.assertIsInstance(payload["modules"], list)

    def test_api_index_shape(self) -> None:
        for fixture_name, artifacts in self._results.items():
            payload = artifacts["API_INDEX.json"]
            self.assertIn("_meta", payload)
            self.assertIn("files", payload)
            self.assertIsInstance(payload["files"], list)

    def test_route_index_shape(self) -> None:
        for fixture_name, artifacts in self._results.items():
            payload = artifacts["ROUTE_INDEX.json"]
            self.assertIn("_meta", payload)
            self.assertIn("files", payload)
            self.assertIsInstance(payload["files"], list)

    def test_config_index_shape(self) -> None:
        for fixture_name, artifacts in self._results.items():
            payload = artifacts["CONFIG_INDEX.json"]
            self.assertIn("_meta", payload)
            self.assertIn("config_keys", payload)
            self.assertIsInstance(payload["config_keys"], list)

    def test_metrics_shape(self) -> None:
        for fixture_name, artifacts in self._results.items():
            payload = artifacts["METRICS.json"]
            for key in ("_meta", "project", "framework", "tokenizer", "artifacts", "repo"):
                self.assertIn(key, payload, f"{key} missing in METRICS ({fixture_name})")
            self.assertIsInstance(payload["artifacts"], list)
            repo = payload["repo"]
            for repo_key in ("source_file_count", "union_source_tokens", "bundle_tokens", "compression_ratio"):
                self.assertIn(repo_key, repo, f"{repo_key} missing in METRICS.repo ({fixture_name})")

    def test_no_absolute_paths_in_artifacts(self) -> None:
        for fixture_name, artifacts in self._results.items():
            for artifact_file, payload in artifacts.items():
                text = json.dumps(payload)
                self.assertNotIn("/Users/", text, f"Local path leaked in {artifact_file} ({fixture_name})")
                self.assertNotIn("/home/", text, f"Local path leaked in {artifact_file} ({fixture_name})")


if __name__ == "__main__":
    unittest.main()
