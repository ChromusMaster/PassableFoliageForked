import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('build_runner', Path(__file__).resolve().parents[1] / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class BuildRunnerTests(unittest.TestCase):
    def test_default_matrix_excludes_beta(self):
        self.assertEqual(build.targets('All', 'All', False), [('Fabric', '26.2'), ('Fabric', '26.3'), ('NeoForge', '26.2')])

    def test_explicit_beta_requires_opt_in(self):
        with self.assertRaises(ValueError):
            build.targets('NeoForge', '26.3', False)
        self.assertEqual(len(build.targets('All', 'All', True)), 4)

    def test_warning_gate(self):
        for line in ['A.java:9: warning: unchecked', 'WARNING: native access', '[12:00] [WARN] loader', '[0.01s][warning][cds] runtime diagnostic', '2 warnings', 'Deprecated Gradle features were used in this build']:
            self.assertIsNotNone(build.WARNING.search(line), line)
        for line in ['0 warnings', '--warning-mode=fail', 'BUILD SUCCESSFUL', 'WarningMode.Fail', 'java --warn-on-artifact-manifest-miss']:
            self.assertIsNone(build.WARNING.search(line), line)


class BuildResultTests(unittest.TestCase):
    def run_fake(self, output, exit_code):
        import contextlib
        import io
        import json
        import tempfile
        from unittest.mock import patch
        class Process:
            stdout = io.StringIO(output)
            def wait(self, timeout=None):
                return exit_code
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(build, 'ROOT', root), patch.object(build.subprocess, 'Popen', return_value=Process()), contextlib.redirect_stdout(io.StringIO()):
                passed = build.run_target('Fabric', '26.2', '2.2', 'partial', False, False)
            report = json.loads((root / 'build/Fabric/26.2/2.2/last-build.json').read_text())
            return passed, report

    def test_warning_rejects_success_exit(self):
        passed, report = self.run_fake('WARNING: plugin diagnostic\nBUILD SUCCESSFUL\n', 0)
        self.assertFalse(passed)
        self.assertEqual(report['status'], 'failed')
        self.assertEqual(len(report['warnings']), 1)

    def test_process_error_is_preserved(self):
        passed, report = self.run_fake('BUILD FAILED\n', 3)
        self.assertFalse(passed)
        self.assertEqual(report['exit_code'], 3)

    def test_partial_success_does_not_claim_jars(self):
        passed, report = self.run_fake('java --warn-on-artifact-manifest-miss\nBUILD SUCCESSFUL\n', 0)
        self.assertTrue(passed)
        self.assertEqual(report['artifacts'], [])
        native = report['command'].index('--enable-native-access=ALL-UNNAMED')
        self.assertLess(native, report['command'].index('org.gradle.wrapper.GradleWrapperMain'))

if __name__ == '__main__':
    unittest.main()
