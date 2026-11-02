"""合成控制器/回执对抗测试；不涉及真实模型或官方成绩。"""
import copy
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "evidence.py"
spec = importlib.util.spec_from_file_location("astra_evidence", MODULE)
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="public_evidence_case_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.receipt = dict(schema=evidence.SCHEMA, run_id="run-1", task_id="fixture-1", arm="G11",
                            seed="42", repo="fixture/repo", base_commit="a" * 40, model_id="synthetic-model",
                            evaluator_id="fixture-controller", evaluator_version="1", evaluator_kind="INDEPENDENT_TEST_RUN",
                            source="synthetic-independent-controller", status="COMPLETE", resolved=True,
                            exit_code=0, error=None, evidence_kind="SYNTHETIC", evaluation_id="eval-1")
        for field in evidence.DIGESTS:
            self.receipt[field] = "b" * 64
        for name, content in [("test_log", b"1 passed\n"), ("raw_patch", b"raw workspace diff\n"),
                              ("patch", b"delivered patch\n"), ("harness_patch", b"delivered patch\n")]:
            filename = name + ".txt"
            (self.root / filename).write_bytes(content)
            self.receipt[name + "_path"] = filename
            self.receipt[name + "_sha256"] = evidence.sha256(content)
        self.row = {k: self.receipt[k] for k in evidence.BIND_FIELDS}
        self.row["evaluator_receipt"] = "receipt.json"
        self.write(self.receipt)
        self.ledger = self.make_ledger()

    def write(self, data):
        raw = json.dumps(data).encode()
        (self.root / "receipt.json").write_bytes(raw)
        self.row["receipt_sha256"] = evidence.sha256(raw)

    def make_ledger(self):
        binding = {k: self.receipt[k] for k in evidence.BIND_FIELDS}
        binding["receipt_sha256"] = self.row["receipt_sha256"]
        return {"schema": evidence.LEDGER_SCHEMA,
                "evaluators": {self.receipt["evaluator_id"]: {k: self.receipt[k] for k in
                    ("evaluator_version", "evaluator_sha256", "evaluator_kind", "source", "evidence_kind")}},
                "bindings": {evidence.identity_key(self.row): binding}}

    def check(self, **kwargs):
        return evidence.validate_receipt(self.row, self.root, kwargs.get("ledger", self.ledger), kwargs.get("seen"))

    def assert_rejected(self, **kwargs):
        value = self.check(**kwargs)
        self.assertNotEqual(value["state"], "EVALUATED")
        self.assertIsNone(value["resolved"])

    def test_controller_bound_synthetic_success(self):
        result = self.check()
        self.assertEqual(result["state"], "EVALUATED")
        self.assertEqual(result["evidence_kind"], "SYNTHETIC")

    def test_genuine_failed_tests_remain_measured_unresolved(self):
        self.receipt.update(resolved=False, exit_code=1)
        self.row.update(resolved=False, exit_code=1)
        self.write(self.receipt)
        self.ledger = self.make_ledger()
        self.assertEqual(self.check()["state"], "EVALUATED")
        self.assertFalse(self.check()["resolved"])

    def test_arbitrary_hash_valid_json_cannot_authenticate(self):
        for data in ({}, {"PASS": True}, {"task": "fixture-1", "arm": "G11"}, [], None, "PASS"):
            with self.subTest(data=data):
                self.write(data)
                self.assert_rejected()

    def test_plausible_self_attestation_has_no_authority(self):
        self.assert_rejected(ledger=None)

    def test_missing_receipt_fields_fail_closed(self):
        for field in evidence.BIND_FIELDS:
            with self.subTest(field=field):
                data = dict(self.receipt)
                del data[field]
                self.write(data)
                self.assert_rejected()

    def test_missing_row_fields_fail_closed(self):
        for field in evidence.BIND_FIELDS:
            with self.subTest(field=field):
                row = dict(self.row)
                del row[field]
                result = evidence.validate_receipt(row, self.root, self.ledger)
                self.assertEqual(result["state"], "UNVERIFIED")

    def test_cross_task_base_model_and_patch_mismatch(self):
        for field in evidence.BIND_FIELDS:
            if not isinstance(self.receipt[field], str):
                continue
            with self.subTest(field=field):
                data = dict(self.receipt)
                data[field] += "-tampered"
                self.write(data)
                self.assert_rejected()

    def test_attacker_changes_both_csv_and_receipt_but_cannot_change_ledger(self):
        self.receipt["base_commit"] = "c" * 40
        self.row["base_commit"] = self.receipt["base_commit"]
        self.write(self.receipt)
        self.assert_rejected()

    def test_wrong_evaluator_version_even_with_new_binding(self):
        self.receipt["evaluator_version"] = "2"
        self.row["evaluator_version"] = "2"
        self.write(self.receipt)
        new = self.make_ledger()
        self.ledger["bindings"] = new["bindings"]
        self.assert_rejected()

    def test_forged_pass_and_infra_exit_codes(self):
        for field, value in [("resolved", "true"), ("resolved", 1), ("exit_code", True),
                             ("exit_code", 1), ("exit_code", 2), ("exit_code", 5),
                             ("error", "timeout")]:
            with self.subTest(field=field, value=value):
                data = dict(self.receipt)
                data[field] = value
                self.write(data)
                self.assert_rejected()

    def test_pytest_collection_error_not_a_repair_failure(self):
        self.receipt.update(resolved=False, exit_code=2)
        self.row.update(resolved=False, exit_code=2)
        self.write(self.receipt)
        self.ledger = self.make_ledger()
        self.assert_rejected()

    def test_missing_log_rejected(self):
        (self.root / "test_log.txt").unlink()
        self.assert_rejected()

    def test_corrupted_log_rejected(self):
        (self.root / "test_log.txt").write_bytes(b"all tests passed forged\n")
        self.assert_rejected()

    def test_empty_log_rejected_even_if_bound(self):
        (self.root / "test_log.txt").write_bytes(b"")
        self.receipt["test_log_sha256"] = evidence.sha256(b"")
        self.row["test_log_sha256"] = self.receipt["test_log_sha256"]
        self.write(self.receipt)
        self.ledger = self.make_ledger()
        self.assert_rejected()

    def test_raw_and_delivered_patch_artifacts_are_verified(self):
        for name in ("raw_patch", "patch", "harness_patch"):
            with self.subTest(name=name):
                path = self.root / (name + ".txt")
                original = path.read_bytes()
                path.write_bytes(b"wrong patch\n")
                self.assert_rejected()
                path.write_bytes(original)

    def test_harness_delivery_mismatch_rejected_even_if_bound(self):
        content = b"different accepted patch\n"
        (self.root / "harness_patch.txt").write_bytes(content)
        self.receipt["harness_patch_sha256"] = evidence.sha256(content)
        self.row["harness_patch_sha256"] = self.receipt["harness_patch_sha256"]
        self.write(self.receipt)
        self.ledger = self.make_ledger()
        self.assert_rejected()

    def test_empty_patch_cannot_claim_repair(self):
        for name in ("raw_patch", "patch", "harness_patch"):
            (self.root / (name + ".txt")).write_bytes(b"")
            self.receipt[name + "_sha256"] = evidence.sha256(b"")
            self.row[name + "_sha256"] = self.receipt[name + "_sha256"]
        self.write(self.receipt)
        self.ledger = self.make_ledger()
        self.assert_rejected()
        # Empty delivery is still an observable unresolved outcome, not missing data.
        self.receipt.update(resolved=False, exit_code=1)
        self.row.update(resolved=False, exit_code=1)
        self.write(self.receipt)
        self.ledger = self.make_ledger()
        self.assertEqual(self.check()["state"], "EVALUATED")
        self.assertFalse(self.check()["resolved"])

    def test_replay_same_receipt(self):
        seen = set()
        self.assertEqual(self.check(seen=seen)["state"], "EVALUATED")
        self.assert_rejected(seen=seen)

    def test_copy_receipt_to_another_run(self):
        self.row["run_id"] = "run-2"
        self.assert_rejected()

    def test_same_evaluation_id_replayed_with_different_run(self):
        seen = set()
        self.check(seen=seen)
        self.row["run_id"] = self.receipt["run_id"] = "run-2"
        self.write(self.receipt)
        self.ledger = self.make_ledger()
        self.assert_rejected(seen=seen)

    def test_untrusted_evaluator(self):
        self.ledger["evaluators"] = {}
        self.assert_rejected()

    def test_unsafe_paths(self):
        for name in ("../escape", "/absolute", "C:/escape", "dir\\escape"):
            with self.subTest(name=name):
                data = dict(self.receipt, test_log_path=name)
                self.write(data)
                self.assert_rejected()

    def test_symlink_artifacts_rejected(self):
        link = self.root / "link.txt"
        try:
            link.symlink_to(self.root / "test_log.txt")
        except OSError:
            self.skipTest("Windows symlink privilege unavailable")
        data = dict(self.receipt, test_log_path="link.txt")
        self.write(data)
        self.assert_rejected()

    def test_duplicate_json_fields_rejected(self):
        raw = json.dumps(self.receipt).encode()[:-1] + b', "resolved": true}'
        (self.root / "receipt.json").write_bytes(raw)
        self.row["receipt_sha256"] = evidence.sha256(raw)
        self.assert_rejected()

    def test_malformed_json_rejected(self):
        (self.root / "receipt.json").write_bytes(b"{broken")
        self.row["receipt_sha256"] = evidence.sha256(b"{broken")
        self.assert_rejected()

    def test_incomplete_execution_is_blocked(self):
        self.row["status"] = "INFRA_ERROR"
        self.assertEqual(self.check()["state"], "BLOCKED")

    def write_csv(self, rows):
        target = self.root / "results.csv"
        with target.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            for raw in rows:
                row = dict(raw)
                row["resolved"] = str(row["resolved"]).lower()
                writer.writerow(row)
        return target

    def test_csv_positive_is_explicitly_synthetic(self):
        result = evidence.verify_experiment_csv(self.write_csv([self.row]), self.root, self.ledger)
        self.assertEqual(result["state"], "EVALUATED")
        self.assertEqual(result["evidence_kind"], "SYNTHETIC")
        self.assertEqual(result["arms"]["G11"]["independent_tasks"], 1)

    def test_csv_duplicate_rows_block_aggregate(self):
        result = evidence.verify_experiment_csv(self.write_csv([self.row, self.row]), self.root, self.ledger)
        self.assertEqual(result["state"], "UNVERIFIED")
        self.assertEqual(result["arms"], {})

    def test_external_ledger_requires_pinned_bytes(self):
        ledger = self.root / "ledger.json"
        ledger.write_text(json.dumps(self.ledger))
        with self.assertRaises(ValueError):
            evidence.load_trusted_ledger(ledger, evidence.sha256(ledger.read_bytes()), self.root)
        receipts = self.root / "receipts"
        receipts.mkdir()
        with self.assertRaises(ValueError):
            evidence.load_trusted_ledger(ledger, "0" * 64, receipts)
        self.assertEqual(evidence.load_trusted_ledger(ledger, evidence.sha256(ledger.read_bytes()), receipts), self.ledger)


if __name__ == "__main__":
    unittest.main()
