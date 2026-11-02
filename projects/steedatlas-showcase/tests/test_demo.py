"""Synthetic offline regression checks: no real historical sources or network calls."""
import sys
from pathlib import Path
import unittest
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import EvidenceRepository, ResearchWorkflow, entity_ids, normalize, validate, synthetic_corpus

class TestQuote(unittest.TestCase):
    def setUp(self): self.p=synthetic_corpus()[0]
    def test_valid(self): self.assertTrue(validate(self.p)[0])
    def test_hash(self): self.assertEqual(validate(replace(self.p,text="改"))[1],"HASH_MISMATCH")
    def test_span(self): self.assertEqual(validate(replace(self.p,span=(0,2)))[1],"QUOTE_MISMATCH")
    def test_revision(self): self.assertEqual(validate(replace(self.p,revision=0))[1],"INVALID_REFERENCE")
    def test_private(self): self.assertEqual(validate(replace(self.p,visibility="PRIVATE"))[1],"RESTRICTED")
    def test_retired(self): self.assertFalse(validate(replace(self.p,active=False))[0])
    def test_rights(self): self.assertEqual(validate(replace(self.p,rights="UNKNOWN"))[1],"RIGHTS_UNKNOWN")
    def test_machine_cannot_approve(self):
        p=synthetic_corpus()[3]
        self.assertTrue(validate(p)[0])
        self.assertEqual(validate(replace(p,relation="SUPPORTS"))[1],"MENTION_NOT_FACT_PROOF")
    def test_unknown_verification(self): self.assertEqual(validate(replace(self.p,verification="UNKNOWN"))[1],"UNKNOWN_VERIFICATION")

class TestRetrieval(unittest.TestCase):
    def setUp(self): self.r=EvidenceRepository()
    def test_alias(self): self.assertEqual(entity_ids("赤雲的出处"),{"red"})
    def test_normalize(self): self.assertEqual(normalize("赤雲馬"),"赤云马")
    def test_top_two(self):
        r=self.r.search("赤云归属",limit=2)
        self.assertEqual({p["relation"] for p in r["hits"]},{"SUPPORTS","CONTRADICTS"})
    def test_top_one_truncated(self): self.assertTrue(self.r.search("赤云归属",limit=1)["coverage"]["opposition_truncated"])
    def test_dependency(self): self.assertEqual(self.r.search("赤云",limit=5)["coverage"]["independent_support_groups"],1)
    def test_literary(self): self.assertEqual(self.r.answer("玄驹",scope="literary")["mode"],"LITERARY_ATTRIBUTED")
    def test_history_excludes_literary(self): self.assertEqual(self.r.search("玄驹",scope="historical")["hits"],[])
    def test_missing_entity(self): self.assertTrue(self.r.search("赤云和玄驹",limit=1)["coverage"]["missing_entities"])
    def test_unknown(self): self.assertEqual(self.r.search("虚无马")["hits"],[])
    def test_unanswerable(self): self.assertEqual(self.r.answer("赤云的出生年月日")["mode"],"INSUFFICIENT")
    def test_conflict(self): self.assertEqual(self.r.answer("赤云归属",limit=3)["mode"],"CONFLICT")
    def test_no_llm(self): self.assertIsNone(self.r.answer("苍岚")["model"])

class TestResearch(unittest.TestCase):
    def setUp(self): self.r=EvidenceRepository()
    def test_run(self):
        out=ResearchWorkflow(self.r).run("赤云")
        self.assertEqual(out["mode"],"RULE_BASED")
        self.assertEqual(len(out["trace"]),4)
    def test_tool_denied(self):
        with self.assertRaises(PermissionError): ResearchWorkflow(self.r).call("run_shell")
    def test_budget(self):
        a=ResearchWorkflow(self.r,max_calls=1)
        a.call("check_coverage")
        with self.assertRaises(RuntimeError): a.call("check_coverage")
    def test_trace_failure(self):
        a=ResearchWorkflow(self.r)
        with self.assertRaises(ValueError): a.call("search_evidence",query="赤云",limit=100)
        self.assertEqual(a.trace[-1]["status"],"FAILED")

if __name__=="__main__": unittest.main()
