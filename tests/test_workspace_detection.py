from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tokensaver.build import build_project
from tokensaver.scanner import scan_project

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "nextjs_python_web_workspace_fixture"
NESTED_FLUTTER_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "nested_flutter_repo_fixture"


class WorkspaceDetectionTests(unittest.TestCase):
    def test_supported_app_plus_composer_backend_is_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mobile = root / "mobile"
            backend = root / "backend"
            (mobile / "lib").mkdir(parents=True)
            backend.mkdir(parents=True)
            (mobile / "pubspec.yaml").write_text("name: demo\n")
            (mobile / "lib" / "main.dart").write_text("void main() {}\n")
            (backend / "composer.json").write_text('{"name":"demo/backend"}\n')

            scan = scan_project(root)
            self.assertEqual(scan.framework, "workspace")
            self.assertIn("mobile/pubspec.yaml", scan.manifests)
            self.assertIn("backend/composer.json", scan.manifests)
            self.assertIn("pub", scan.package_managers)
            self.assertIn("composer", scan.package_managers)

    def test_nested_flutter_project_is_not_misclassified_as_workspace(self) -> None:
        scan = scan_project(NESTED_FLUTTER_FIXTURE)
        self.assertEqual(scan.framework, "flutter")
        self.assertIn("mobile/pubspec.yaml", scan.manifests)
        self.assertIn("mobile/lib/main.dart", scan.entrypoints)

    def test_detects_nested_workspace(self) -> None:
        scan = scan_project(WORKSPACE_FIXTURE)
        self.assertEqual(scan.framework, "workspace")
        self.assertIn("frontend/package.json", scan.manifests)
        self.assertIn("backend/pyproject.toml", scan.manifests)
        self.assertIn("frontend/src/app/page.tsx", scan.entrypoints)
        self.assertIn("backend/app/main.py", scan.entrypoints)
        self.assertIn("npm", scan.package_managers)

    def test_builds_combined_workspace_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = build_project(WORKSPACE_FIXTURE, output_dir=temp_dir)

            self.assertEqual(result["scan"].framework, "workspace")
            self.assertEqual(result["plugin"], "workspace")

            api_index = json.loads((Path(temp_dir) / "API_INDEX.json").read_text())
            route_index = json.loads((Path(temp_dir) / "ROUTE_INDEX.json").read_text())
            config_index = json.loads((Path(temp_dir) / "CONFIG_INDEX.json").read_text())
            commands = json.loads((Path(temp_dir) / "COMMANDS.json").read_text())

            api_rows = [
                (group[0], entry[0], entry[2])
                for group in api_index["files"]
                for entry in group[2]
            ]
            route_rows = [
                (group[0], entry[0])
                for group in route_index["files"]
                for entry in group[1]
            ]
            config_keys = {item["name"] for item in config_index["config_keys"]}
            command_rows = {(item["name"], item["cwd"]) for item in commands["commands"]}

            self.assertIn(("frontend/src/app/api/health/route.ts", "/api/health", "GET"), api_rows)
            self.assertIn(("backend/app/main.py", "/health", "GET"), api_rows)
            self.assertIn(("frontend/src/app/page.tsx", "/"), route_rows)
            self.assertIn(("backend/app/main.py", "/health"), route_rows)
            self.assertIn("NEXT_PUBLIC_API_BASE_URL", config_keys)
            self.assertIn("BACKEND_API_KEY", config_keys)
            self.assertIn(("frontend:dev", "frontend"), command_rows)
            self.assertIn(("backend:test", "backend"), command_rows)


if __name__ == "__main__":
    unittest.main()
