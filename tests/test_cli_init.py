from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tokensaver_cli import cmd_init


REPO_ROOT = Path(__file__).resolve().parents[1]
NODE_FIXTURE = REPO_ROOT / "benchmarks" / "fixtures" / "node_fixture"


class CliInitTests(unittest.TestCase):
    def test_init_builds_bundle_and_installs_integrations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_copy = Path(temp_dir) / "node-fixture"
            shutil.copytree(NODE_FIXTURE, repo_copy)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = cmd_init(str(repo_copy))

            output = stdout.getvalue()
            artifact_dir = repo_copy / "docs" / "tokensaver"

            self.assertIn("TokenSaver Init", output)
            self.assertIn("Compression:", output)
            self.assertEqual(result["plugin"], "generic")
            self.assertTrue((artifact_dir / "METRICS.json").exists())
            self.assertTrue((repo_copy / ".cursor" / "rules" / "tokensaver.mdc").exists())
            self.assertTrue((repo_copy / "CLAUDE.md").exists())
            self.assertTrue((repo_copy / "AGENTS.md").exists())
            self.assertTrue((repo_copy / ".windsurfrules").exists())

            metrics = json.loads((artifact_dir / "METRICS.json").read_text())
            self.assertGreater(metrics["repo"]["bundle_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
