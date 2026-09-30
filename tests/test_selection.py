import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('selection',Path(__file__).parents[1]/'scripts/select_batch.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Selection(unittest.TestCase):
    def setUp(self):
        self.now=m.timestamp('2026-10-30T12:00:00Z')
        self.data={'candidates':[{'id':str(i),'segment':'a' if i%2 else 'b','eligible':True} for i in range(30)],'observations':[]}
    def test_reproducible_exploration_and_no_duplicates(self):
        a=m.select(self.data,self.now,seed=42)
        self.assertEqual(a,m.select(self.data,self.now,seed=42))
        self.assertEqual(len({r['id'] for r in a['selected']}),10)
        self.assertEqual(sum(r['route']=='explore' for r in a['selected']),2)
    def test_ineligible_and_contacted_excluded(self):
        self.data['candidates'][0]['eligible']=False
        self.data['observations']=[{'id':'1','segment':'a','sent_at':'2026-10-29T00:00:00Z'}]
        ids={r['id'] for r in m.select(self.data,self.now,size=30)['selected']}
        self.assertNotIn('0',ids);self.assertNotIn('1',ids)
    def test_mature_and_missing_outcomes(self):
        base={'segment':'a','sent_at':'2026-10-01T00:00:00Z','observed_through':'2026-10-20T00:00:00Z'}
        self.data['observations']=[dict(base,id='old1',qualified_reply_within_window=True),dict(base,id='old2',qualified_reply_within_window=False),dict(base,id='old3',qualified_reply_within_window=None)]
        result=m.select(self.data,self.now)
        self.assertEqual(result['posteriors'],{'a':[2,2]})
        self.assertEqual(result['censored_observations'],1)
    def test_recent_positive_not_early_success_bias(self):
        self.data['observations']=[{'id':'old','segment':'a','sent_at':'2026-10-29T00:00:00Z','observed_through':self.now.isoformat(),'qualified_reply_within_window':True}]
        self.assertEqual(m.select(self.data,self.now)['posteriors'],{})
    def test_duplicates_rejected(self):
        self.data['candidates'].append(self.data['candidates'][0])
        with self.assertRaises(ValueError):m.select(self.data,self.now)

if __name__=='__main__':unittest.main()
