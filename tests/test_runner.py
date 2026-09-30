import fcntl
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('runner',Path(__file__).parents[1]/'scripts/run_campaign.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Runner(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'prompts').mkdir();(self.root/'prompts/daily.md').write_text('Read AGENTS.md')
        self.c=self.root/'campaigns/test';self.c.mkdir(parents=True)
        (self.c/'campaign.json').write_text('{}')
        self.config=self.c/'runner.json'
    def tearDown(self): self.tmp.cleanup()
    def config_for(self,code,timeout=5):
        self.config.write_text(json.dumps({'argv':[sys.executable,'-c',code],'timeout_seconds':timeout}))
    def status(self):return json.loads(next((self.c/'runs').glob('*/status.json')).read_text())
    def test_prompt_delivery_and_logs(self):
        self.config_for('import sys; p=sys.stdin.read(); assert "Selected campaign directory:" in p; print("ok")')
        self.assertEqual(m.run(self.config,self.root),0)
        self.assertEqual(self.status()['status'],'completed')
        self.assertEqual(next((self.c/'runs').glob('*/output.log')).read_text().strip(),'ok')
    def test_failure_propagated_no_retry(self):
        self.config_for('raise SystemExit(7)')
        self.assertEqual(m.run(self.config,self.root),7)
        self.assertEqual(len(list((self.c/'runs').iterdir())),1)
    def test_timeout_recorded(self):
        self.config_for('import time;time.sleep(10)',1)
        self.assertEqual(m.run(self.config,self.root),124)
        self.assertEqual(self.status()['status'],'timed_out')
    def test_overlap_skipped(self):
        self.config_for('raise SystemExit(0)')
        (self.root/'.runtime').mkdir()
        with (self.root/'.runtime/agent.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.assertEqual(m.run(self.config,self.root),75)
        self.assertFalse((self.c/'runs').exists())

if __name__=='__main__':unittest.main()
