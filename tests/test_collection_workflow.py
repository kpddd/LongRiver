"""Execute the workflow's final gate for successful and failed runner outcomes."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


WORKFLOW = Path(__file__).parents[1] / ".github/workflows/collect-data.yml"
BASH = shutil.which("bash")
if os.name == "nt":
    git = shutil.which("git")
    git_bash = Path(git).parents[1] / "bin/bash.exe" if git else None
    BASH = str(git_bash) if git_bash and git_bash.is_file() else None


@unittest.skipUnless(BASH, "Bash is required to execute the Actions result gate")
class CollectionResultTests(unittest.TestCase):
    def check_result(self, primary, collected, fallback, recovered, expected):
        # Extract the actual run block, so changes to the deployed gate are tested.
        step = WORKFLOW.read_text(encoding="utf-8").split(
            "      - name: Check collection result\n", 1
        )[1]
        script = textwrap.dedent(step.split("        run: |\n", 1)[1].split("\n\n", 1)[0])
        with tempfile.TemporaryDirectory() as directory:
            summary = Path(directory) / "summary.md"
            result = subprocess.run(
                [BASH, "-e", "-c", script],
                env={
                    **os.environ,
                    "PRIMARY_RESULT": primary,
                    "PRIMARY_COLLECTED": collected,
                    "FALLBACK_RESULT": fallback,
                    "FALLBACK_COLLECTED": recovered,
                    "GITHUB_STEP_SUMMARY": summary.as_posix(),
                },
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            if expected == 0:
                self.assertIn("observations", summary.read_text())
            else:
                self.assertIn("::error::", result.stdout)

    def test_primary_success_with_skipped_fallback(self):
        self.check_result("success", "true", "skipped", "", 0)

    def test_fallback_recovers_failed_collection(self):
        self.check_result("success", "false", "success", "true", 0)

    def test_both_collections_fail_despite_continue_on_error(self):
        self.check_result("success", "false", "success", "false", 1)

    def test_setup_or_test_failure_is_fatal(self):
        self.check_result("failure", "", "skipped", "", 1)

    def test_push_failure_after_fetch_is_fatal(self):
        self.check_result("failure", "true", "skipped", "", 1)

    def test_fallback_push_failure_is_fatal(self):
        self.check_result("success", "false", "failure", "true", 1)

    def test_missing_outputs_cannot_report_success(self):
        self.check_result("success", "", "skipped", "", 1)
