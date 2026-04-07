"""Usefulness tests for TokenSaver artifacts.

These tests verify that build outputs are meaningfully useful for each
supported stack — not just structurally correct, but containing enough
extracted data to serve a coding agent.

For first-class stacks (flutter, react_native):
  - module_graph must be non-empty
  - commands must be present
  - at least one of api_index, route_index, config_index must be non-empty

For generic supported stacks (python, node, nextjs):
  - module_graph must be non-empty
  - commands must be non-empty
  - at least one of api_index, route_index, config_index must be non-empty
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tokensaver.build import build_project

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "benchmarks" / "fixtures"

FIRST_CLASS_FIXTURES = {
    "flutter": FIXTURES_DIR / "flutter_fixture",
    "react_native": FIXTURES_DIR / "react_native_fixture",
    "fastapi": FIXTURES_DIR / "fastapi_fixture",
    "django": FIXTURES_DIR / "django_fixture",
    "spring_boot": FIXTURES_DIR / "spring_boot_fixture",
    "go": FIXTURES_DIR / "go_fixture",
}

GENERIC_SUPPORTED_FIXTURES = {
    "python": FIXTURES_DIR / "python_fixture",
    "node": FIXTURES_DIR / "node_fixture",
    "nextjs": FIXTURES_DIR / "nextjs_fixture",
}


def _build_artifacts(fixture_path: Path) -> dict[str, dict]:
    with tempfile.TemporaryDirectory() as temp_dir:
        build_project(fixture_path, output_dir=temp_dir)
        artifacts = {}
        for path in Path(temp_dir).glob("*.json"):
            artifacts[path.stem] = json.loads(path.read_text())
    return artifacts


class FirstClassUsefulnessTests(unittest.TestCase):
    """Verify first-class stacks produce meaningfully useful artifacts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._builds: dict[str, dict[str, dict]] = {}
        for name, path in FIRST_CLASS_FIXTURES.items():
            cls._builds[name] = _build_artifacts(path)

    def test_module_graph_non_empty(self) -> None:
        for name, arts in self._builds.items():
            modules = arts["MODULE_GRAPH"]["modules"]
            self.assertGreater(
                len(modules), 0,
                f"{name}: module_graph should contain at least one module",
            )

    def test_commands_non_empty(self) -> None:
        for name, arts in self._builds.items():
            commands = arts["COMMANDS"]["commands"]
            self.assertGreater(
                len(commands), 0,
                f"{name}: commands should contain at least one command",
            )

    def test_at_least_one_domain_artifact_non_empty(self) -> None:
        for name, arts in self._builds.items():
            api_count = len(arts["API_INDEX"].get("files", []))
            route_count = len(arts["ROUTE_INDEX"].get("files", []))
            config_count = len(arts["CONFIG_INDEX"].get("config_keys", []))
            total = api_count + route_count + config_count
            self.assertGreater(
                total, 0,
                f"{name}: at least one of api_index, route_index, or config_index "
                f"should be non-empty (api={api_count}, routes={route_count}, config={config_count})",
            )

    def test_module_graph_has_tokens(self) -> None:
        for name, arts in self._builds.items():
            for mod in arts["MODULE_GRAPH"]["modules"]:
                self.assertGreater(
                    mod.get("tokens", 0), 0,
                    f"{name}: module '{mod['name']}' should have positive token count",
                )


class GenericSupportedUsefulnessTests(unittest.TestCase):
    """Verify generic supported stacks produce meaningfully useful artifacts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._builds: dict[str, dict[str, dict]] = {}
        for name, path in GENERIC_SUPPORTED_FIXTURES.items():
            cls._builds[name] = _build_artifacts(path)

    def test_module_graph_non_empty(self) -> None:
        for name, arts in self._builds.items():
            modules = arts["MODULE_GRAPH"]["modules"]
            self.assertGreater(
                len(modules), 0,
                f"{name}: module_graph should contain at least one module",
            )

    def test_commands_non_empty(self) -> None:
        for name, arts in self._builds.items():
            commands = arts["COMMANDS"]["commands"]
            self.assertGreater(
                len(commands), 0,
                f"{name}: commands should contain at least one command",
            )

    def test_at_least_one_domain_artifact_non_empty(self) -> None:
        for name, arts in self._builds.items():
            api_count = len(arts["API_INDEX"].get("files", []))
            route_count = len(arts["ROUTE_INDEX"].get("files", []))
            config_count = len(arts["CONFIG_INDEX"].get("config_keys", []))
            total = api_count + route_count + config_count
            self.assertGreater(
                total, 0,
                f"{name}: at least one of api_index, route_index, or config_index "
                f"should be non-empty (api={api_count}, routes={route_count}, config={config_count})",
            )

    def test_config_index_has_entries_for_backend_stacks(self) -> None:
        for name in ("python", "node"):
            arts = self._builds[name]
            config_keys = arts["CONFIG_INDEX"].get("config_keys", [])
            self.assertGreater(
                len(config_keys), 0,
                f"{name}: config_index should extract environment variable references",
            )

    def test_api_or_route_index_non_empty_for_backend_stacks(self) -> None:
        for name in ("python", "node"):
            arts = self._builds[name]
            api_count = len(arts["API_INDEX"].get("files", []))
            route_count = len(arts["ROUTE_INDEX"].get("files", []))
            self.assertGreater(
                api_count + route_count, 0,
                f"{name}: backend stacks should have api_index or route_index entries",
            )

    def test_nextjs_has_file_based_routes(self) -> None:
        arts = self._builds["nextjs"]
        route_files = arts["ROUTE_INDEX"].get("files", [])
        self.assertGreater(
            len(route_files), 0,
            "nextjs: route_index should extract file-based routes from app/ directory",
        )


if __name__ == "__main__":
    unittest.main()
