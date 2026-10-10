"""Optional offline Gradle integration: set GRADLE_TEST_COMMAND to a JSON argv list."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ADVANCEMENT = 'data/passablefoliage/advancement/recipes/misc/leaf_walker.json'


@unittest.skipUnless(os.environ.get('GRADLE_TEST_COMMAND'), 'Set GRADLE_TEST_COMMAND for Gradle resource integration')
class ResourceBuildTests(unittest.TestCase):
    def test_versioned_outputs_and_reject_wrong_schema(self):
        command = json.loads(os.environ['GRADLE_TEST_COMMAND'])
        build_text = (ROOT / 'build.gradle').read_text(encoding='utf-8')
        resource_config = build_text.split('def metadata = ', 1)[1].split('tasks.withType(JavaCompile)', 1)[0]
        with tempfile.TemporaryDirectory(prefix='pf-resource-test-') as directory:
            project = Path(directory)
            for relative in ['src/main/resources', 'src/generated/resources', 'src/fabric/resources', 'src/neoforge/resources', 'gradle']:
                shutil.copytree(ROOT / relative, project / relative)
            # Compact input ensures conversion parses JSON instead of replacing lines.
            for relative in ['src/generated/resources', 'src/neoforge/resources']:
                path = project / relative / ADVANCEMENT
                path.write_text(json.dumps(json.loads(path.read_text(encoding='utf-8'))), encoding='utf-8')
            (project / 'settings.gradle').write_text("rootProject.name = 'resource-regression'\n", encoding='utf-8')
            (project / 'gradle.properties').write_text(
                'org.gradle.jvmargs=-Xmx512m --enable-native-access=ALL-UNNAMED\norg.gradle.workers.max=2\n',
                encoding='utf-8')
            (project / 'build.gradle').write_text(
                "plugins { id 'java' }\n"
                "def loader = providers.gradleProperty('modloader').get()\n"
                "def mc = providers.gradleProperty('minecraft_version').get()\n"
                "def fabricApi = '0.0.0'\ndef neoVersion = '0.0.0'\nversion = 'test'\n"
                "apply from: 'gradle/source-layout.gradle'\n"
                "def metadata = " + resource_config +
                "tasks.register('partialCheck')\napply from: 'gradle/advancements.gradle'\n",
                encoding='utf-8')

            def run(loader, mc, label, *tasks):
                result = subprocess.run(
                    command + ['-p', str(project), '--offline', '--no-daemon', '--console=plain',
                               '--warning-mode=fail', f'-Pmodloader={loader}', f'-Pminecraft_version={mc}', *tasks],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', timeout=120)
                if os.environ.get('RESOURCE_TEST_LOG_DIR'):
                    logdir = Path(os.environ['RESOURCE_TEST_LOG_DIR']) / loader / mc
                    logdir.mkdir(parents=True, exist_ok=True)
                    (logdir / (label + '.log')).write_text(result.stdout, encoding='utf-8')
                return result

            for loader in ['Fabric', 'NeoForge']:
                for index, mc in enumerate(['26.3', '26.2', '26.3']):
                    with self.subTest(loader=loader, minecraft=mc, pass_number=index):
                        result = run(loader, mc, f'resources-{index}', 'jar', 'partialCheck')
                        self.assertEqual(result.returncode, 0, result.stdout)
                        self.assertNotRegex(result.stdout, r'(?im)(\bwarning\s*:|\[warning\]|Deprecated Gradle features)')
                        archive = project / 'build/libs/resource-regression-test.jar'
                        with zipfile.ZipFile(archive) as jar:
                            self.assertEqual(jar.namelist().count(ADVANCEMENT), 1)
                            actual = json.loads(jar.read(ADVANCEMENT))
                        source_dir = 'src/generated/resources' if loader == 'Fabric' else 'src/neoforge/resources'
                        expected = json.loads((ROOT / source_dir / ADVANCEMENT).read_text(encoding='utf-8'))
                        expected['criteria']['has_the_recipe']['conditions'] = {
                            'recipe' if mc == '26.2' else 'recipes': 'passablefoliage:leaf_walker'}
                        self.assertEqual(actual, expected)

            # Reproduce the bad-version payload in processed output and require rejection.
            processed = project / 'build/resources/main' / ADVANCEMENT
            data = json.loads(processed.read_text(encoding='utf-8'))
            data['criteria']['has_the_recipe']['conditions'] = {'recipe': 'passablefoliage:leaf_walker'}
            processed.write_text(json.dumps(data), encoding='utf-8')
            result = run('NeoForge', '26.3', 'expected-rejection', 'verifyAdvancementResources', '-x', 'processResources')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Invalid recipe unlock criterion', result.stdout)


if __name__ == '__main__':
    unittest.main()
