import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def translate(value):
    if isinstance(value, dict):
        return {('type' if k == 'condition' else k): (v.replace('fabric:', 'neoforge:') if k == 'condition' else translate(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [translate(v) for v in value]
    return value


class ResourceTests(unittest.TestCase):
    def test_platform_conditions_match(self):
        found = 0
        for path in (ROOT / 'src/generated/resources').rglob('*.json'):
            original = json.loads(path.read_text())
            if 'fabric:load_conditions' not in original:
                continue
            found += 1
            expected = dict(original)
            expected['neoforge:conditions'] = translate(expected.pop('fabric:load_conditions'))
            counterpart = ROOT / 'src/neoforge/resources' / path.relative_to(ROOT / 'src/generated/resources')
            self.assertEqual(json.loads(counterpart.read_text()), expected, str(path))
        self.assertEqual(found, 3)

    def test_every_mixin_has_source(self):
        config = json.loads((ROOT / 'src/main/resources/passablefoliage.mixins.json').read_text())
        for name in config['mixins'] + config['client']:
            relative = Path(*(config['package'] + '.' + name).split('.')).with_suffix('.java')
            for mc in ['26.2', '26.3']:
                self.assertTrue((ROOT / 'src/main/java' / relative).is_file() or (ROOT / f'src/version/{mc}/java' / relative).is_file(), name)
        self.assertEqual(config['injectors']['defaultRequire'], 1)

    def test_shared_sources_do_not_import_loader_apis(self):
        for path in (ROOT / 'src/main/java').rglob('*.java'):
            text = path.read_text()
            self.assertNotIn('import net.fabricmc.', text, str(path))
            self.assertNotIn('import net.neoforged.', text, str(path))

if __name__ == '__main__':
    unittest.main()
