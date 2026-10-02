import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import timedelta

spec = importlib.util.spec_from_file_location('campaign', Path(__file__).parents[1]/'scripts/campaign.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class Gates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = m.connect(self.tmp.name)
        self.now = m.stamp('2026-10-10T12:00:00-07:00')
        self.c = json.loads((Path(__file__).parents[1]/'examples/campaign.json').read_text())
        self.c.update(send_authorized=True, paused=False, reconciled_at=self.now.isoformat())
    def tearDown(self):
        self.db.close(); self.tmp.cleanup()
    def add(self, n, at=None, cohort='c1'):
        self.db.execute('INSERT INTO invitations VALUES (?,?,?,?,?,?)',
          (f'https://www.linkedin.com/in/p{n}/','sent',(at or self.now).isoformat(),cohort,'note','observed'))
    def test_default_draft(self):
        self.c['send_authorized']=False
        self.assertFalse(m.gate(self.c,self.db,self.now)['allowed'])
    def test_hold_and_stale_reconciliation(self):
        self.c['not_before']=(self.now+timedelta(days=1)).isoformat()
        self.assertFalse(m.gate(self.c,self.db,self.now)['allowed'])
        self.c['not_before']=None
        self.c['reconciled_at']=(self.now-timedelta(hours=25)).isoformat()
        self.assertFalse(m.gate(self.c,self.db,self.now)['allowed'])
    def test_daily_cap(self):
        for i in range(10): self.add(i)
        self.assertIn('Daily cap reached',m.gate(self.c,self.db,self.now)['reasons'])
    def test_explicit_history_override_expires_and_preserves_unknown_gate(self):
        self.c['reconciled_at']=None
        self.c['history_override']={'approved': True, 'user_instruction': 'Proceed with incomplete history',
            'approved_at': self.now.isoformat(), 'expires_at': (self.now+timedelta(hours=1)).isoformat()}
        self.assertTrue(m.gate(self.c,self.db,self.now)['allowed'])
        self.assertFalse(m.gate(self.c,self.db,self.now+timedelta(hours=1))['allowed'])
        m.reserve(self.c,self.db,self.now,'https://www.linkedin.com/in/test/','c1','note')
        m.resolve(self.db,self.now,'https://www.linkedin.com/in/test/','unknown','No confirmation')
        self.assertFalse(m.gate(self.c,self.db,self.now)['allowed'])
    def test_rolling_boundary(self):
        self.c['cohort_size']=100
        for i in range(50): self.add(i,self.now-timedelta(days=6))
        self.assertFalse(m.gate(self.c,self.db,self.now)['allowed'])
        later=self.now+timedelta(days=1)
        self.c['reconciled_at']=later.isoformat()
        self.assertTrue(m.gate(self.c,self.db,later)['allowed'])
    def test_timezone_midnight(self):
        self.add(1,m.stamp('2026-10-10T06:59:59Z'))
        self.assertEqual(m.gate(self.c,self.db,self.now)['sent_today'],0)
    def test_crash_reservation_blocks_second_connection(self):
        url='https://ca.linkedin.com/in/Alice/?trk=x'
        m.reserve(self.c,self.db,self.now,url,'c1','note')
        other=m.connect(self.tmp.name)
        with self.assertRaises(ValueError):
            m.reserve(self.c,other,self.now,'https://www.linkedin.com/in/bob/','c1','note')
        other.close()
        m.resolve(self.db,self.now,url,'unknown','No confirmation')
        self.assertFalse(m.gate(self.c,self.db,self.now)['allowed'])
        m.resolve(self.db,self.now,url,'sent','Pending verified')
        with self.assertRaises(ValueError): m.reserve(self.c,self.db,self.now,url,'c1','note')
    def test_cohort_requires_mature_audit(self):
        self.c['cohort_size']=1
        self.add(1,self.now-timedelta(days=8))
        self.assertFalse(m.gate(self.c,self.db,self.now)['allowed'])
        self.db.execute('INSERT INTO audit_events (cohort,at,decision,evidence) VALUES (?,?,?,?)',('c1',self.now.isoformat(),'continue','report'))
        self.assertTrue(m.gate(self.c,self.db,self.now)['allowed'])
    def test_audit_pause_always_holds(self):
        self.add(1,self.now-timedelta(days=8))
        self.db.execute('INSERT INTO audit_events (cohort,at,decision,evidence) VALUES (?,?,?,?)',('c1',self.now.isoformat(),'pause','poor fit'))
        self.assertFalse(m.gate(self.c,self.db,self.now)['allowed'])
    def test_message_and_profile_validation(self):
        with self.assertRaises(ValueError): m.profile('https://linkedin.com.evil/in/alice')
        with self.assertRaises(ValueError):
            m.reserve(self.c,self.db,self.now,'https://www.linkedin.com/in/a/','c1','😀'*151)
    def test_missing_legacy_history_blocks(self):
        self.c['audit_required_cohorts']=['legacy']
        result=m.gate(self.c,self.db,self.now)
        self.assertFalse(result['allowed'])
        self.assertEqual(result['remaining_today'],0)
    def test_cohort_rotation_rejected(self):
        self.add(1)
        with self.assertRaises(ValueError):
            m.reserve(self.c,self.db,self.now,'https://www.linkedin.com/in/new/','c2','note')
    def test_pending_after_uncertain_attempt_counts(self):
        url='https://www.linkedin.com/in/alice/'
        m.reserve(self.c,self.db,self.now,url,'c1','note')
        m.resolve(self.db,self.now,url,'unknown','Timeout')
        m.resolve(self.db,self.now,url,'already_pending','Pending visible')
        self.assertEqual(m.gate(self.c,self.db,self.now)['sent_today'],1)
    def test_latest_audit_supersedes_pause_but_history_remains(self):
        self.add(1,self.now-timedelta(days=8))
        for decision in ['pause','continue']:
            self.db.execute('INSERT INTO audit_events (cohort,at,decision,evidence) VALUES (?,?,?,?)',('c1',self.now.isoformat(),decision,'report'))
        self.assertTrue(m.gate(self.c,self.db,self.now)['allowed'])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM audit_events').fetchone()[0],2)
    def test_naive_time_rejected(self):
        with self.assertRaises(ValueError): m.stamp('2026-10-10T12:00:00')

if __name__=='__main__': unittest.main()
