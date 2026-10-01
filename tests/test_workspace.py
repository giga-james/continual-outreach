import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workspace', ROOT/'scripts/workspace.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.host = self.base/'product with spaces'
        self.host.mkdir()
        self.state = self.base/'private-state'

    def tearDown(self):
        self.tmp.cleanup()

    def test_install_preserves_host_instructions_and_is_idempotent(self):
        (self.host/'AGENTS.md').write_text('Host rules')
        (self.host/'CLAUDE.md').write_text('Host Claude rules')
        first = m.install(self.host)
        self.assertEqual(m.install(self.host), first)
        self.assertEqual((self.host/'AGENTS.md').read_text(), 'Host rules')
        self.assertEqual((self.host/'CLAUDE.md').read_text(), 'Host Claude rules')
        self.assertEqual(len(first['loaders']), 2)
        for path in first['loaders']:
            self.assertIn(str(ROOT), Path(path).read_text())
        self.assertFalse((self.host/'campaigns').exists())

    def test_collision_preflight_does_not_partially_install(self):
        target = self.host/'.claude/skills/continual-outreach/SKILL.md'
        target.parent.mkdir(parents=True)
        target.write_text('User-owned skill')
        with self.assertRaises(ValueError):
            m.install(self.host)
        self.assertFalse((self.host/'.agents').exists())
        self.assertEqual(target.read_text(), 'User-owned skill')

    def test_symlink_does_not_modify_other_workspace(self):
        other = self.base/'other'
        other.mkdir()
        (self.host/'.agents').symlink_to(other, target_is_directory=True)
        with self.assertRaises(ValueError):
            m.install(self.host)
        self.assertEqual(list(other.iterdir()), [])

    def test_private_state_resumes_without_resetting_authorization(self):
        result = m.initialize(self.host, 'discovery', self.state)
        campaign = Path(result['campaign_dir'])
        config_path = campaign/'campaign.json'
        config = json.loads(config_path.read_text())
        self.assertFalse(config['send_authorized'])
        self.assertTrue(config['paused'])
        config['name'] = 'Changed by user'
        config_path.write_text(json.dumps(config))
        self.assertEqual(m.initialize(self.host, 'discovery', self.state), result)
        self.assertEqual(json.loads(config_path.read_text())['name'], 'Changed by user')
        self.assertEqual(list(self.host.iterdir()), [])

    def test_distinct_workspaces_isolate_campaigns(self):
        other = self.base/'other'
        other.mkdir()
        a = m.initialize(self.host, 'same-name', self.state)
        b = m.initialize(other, 'same-name', self.state)
        self.assertNotEqual(a['campaign_dir'], b['campaign_dir'])

    def test_reject_unsafe_names_and_state_inside_source(self):
        for name in ['../escape', '', 'has spaces']:
            with self.assertRaises(ValueError):
                m.initialize(self.host, name, self.state)
        for state in [self.host/'private', ROOT/'private']:
            with self.assertRaises(ValueError):
                m.initialize(self.host, 'discovery', state)

    def test_mismatched_binding_never_overwrites(self):
        result = m.initialize(self.host, 'discovery', self.state)
        binding = Path(result['campaign_dir'])/'workspace.json'
        binding.write_text('{}')
        with self.assertRaises(ValueError):
            m.initialize(self.host, 'discovery', self.state)
        self.assertEqual(binding.read_text(), '{}')


if __name__ == '__main__':
    unittest.main()
