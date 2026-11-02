"""G11 评测回执门禁：完整性与独立控制器来源必须同时成立。

trusted_ledger 是由评测控制器独立保管的可信输入，不能由待评 Agent 生成。
本模块不签发信任、不执行测试、不把任意哈希当成来源认证。
CLI 额外要求账本位于 receipt_root 外，且由调用者提供预先固定的 SHA256。
该隔离检查不等同于 OS 权限隔离；部署者必须禁止 Agent 修改账本和评测器。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath

SCHEMA = "astra-evaluation-receipt-v1"
LEDGER_SCHEMA = "astra-controller-ledger-v1"
IDENTITY = ("run_id", "task_id", "arm", "seed")
BIND_FIELDS = IDENTITY + (
    "repo", "base_commit", "task_sha256", "model_id", "model_sha256",
    "config_sha256", "candidate_sha256", "raw_patch_sha256", "patch_sha256",
    "harness_patch_sha256", "evaluator_id", "evaluator_version", "evaluator_sha256",
    "evaluator_kind", "source", "test_log_sha256", "status", "resolved",
    "exit_code", "error", "evidence_kind", "evaluation_id",
)
DIGESTS = tuple(k for k in BIND_FIELDS if k.endswith("_sha256"))
KINDS = {"INDEPENDENT_TEST_RUN", "OFFICIAL_SCORER"}
MISSING = {"REQUESTED", "NOT_RUN", "BLOCKED", "INFRA_ERROR"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity_key(row: dict) -> str:
    # JSON encoding prevents delimiter collisions in task/run names.
    return json.dumps([row[k] for k in IDENTITY], ensure_ascii=False, separators=(",", ":"))


def strict_json(raw: bytes) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON field")
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON")))
    if type(value) is not dict:
        raise ValueError("JSON object required")
    return value


def read_artifact(root: Path, name: str, limit: int = 16_000_000) -> bytes:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("unsafe artifact path")
    rel = PurePosixPath(name)
    if rel.is_absolute() or any(p in {"..", "."} for p in rel.parts):
        raise ValueError("unsafe artifact path")
    target = root.joinpath(*rel.parts)
    # Refuse symlinks even when their current target happens to remain inside root.
    for part in [target, *target.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ValueError("symlink artifact")
    target = target.resolve(strict=True)
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError("artifact outside root")
    with target.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("artifact too large")
    return data


def _normal_row(row: dict) -> dict:
    result = dict(row)
    for name in BIND_FIELDS:
        if name not in result:
            raise ValueError("missing row field:" + name)
    # CSV strings have a single explicit representation; no truthiness coercion.
    if result["resolved"] in ("true", "false"):
        result["resolved"] = result["resolved"] == "true"
    if isinstance(result["exit_code"], str) and re.fullmatch(r"-?\d+", result["exit_code"]):
        result["exit_code"] = int(result["exit_code"])
    if result["error"] == "":
        result["error"] = None
    return result


def validate_receipt(row: dict, receipt_root: Path, trusted_ledger: dict | None,
                     seen: set | None = None) -> dict:
    """返回 EVALUATED 或 UNVERIFIED/BLOCKED；失败时 resolved 必为 None。

    seen 由单次分析控制器持有；同时拒绝 identity、evaluation_id、receipt hash 重复。
    跨批次重放通过预冻结 run_id/ledger 拒绝；跨进程全局唯一性需控制器持久化。
    """
    def reject(reason, state="UNVERIFIED"):
        return {"state": state, "resolved": None, "reason": reason}
    if row.get("status") in MISSING:
        return reject("evaluation_not_completed:" + row["status"], "BLOCKED")
    try:
        x = _normal_row(row)
        root = Path(receipt_root).resolve(strict=True)
        raw = read_artifact(root, x["evaluator_receipt"], 1_000_000)
        digest = sha256(raw)
        if digest != x.get("receipt_sha256"):
            return reject("receipt_sha_mismatch")
        receipt = strict_json(raw)
        if receipt.get("schema") != SCHEMA:
            return reject("unknown_receipt_schema")
        for field in BIND_FIELDS:
            if field not in receipt or type(receipt[field]) is not type(x[field]) or receipt[field] != x[field]:
                return reject("row_binding_mismatch:" + field)
        for field in IDENTITY + ("repo", "model_id", "evaluator_id", "evaluator_version", "source", "evaluation_id"):
            value = receipt[field]
            if type(value) is not str or not value or value != value.strip():
                return reject("invalid_identity:" + field)
        if not re.fullmatch(r"[0-9a-f]{40}", receipt["base_commit"]):
            return reject("invalid_base_commit")
        for field in DIGESTS:
            if type(receipt[field]) is not str or not re.fullmatch(r"[0-9a-f]{64}", receipt[field]):
                return reject("invalid_digest:" + field)
        if receipt["evaluator_kind"] not in KINDS or receipt["evidence_kind"] not in {"REAL", "SYNTHETIC"}:
            return reject("invalid_evidence_kind")
        if receipt["status"] != "COMPLETE" or type(receipt["resolved"]) is not bool:
            return reject("not_a_completed_evaluation")
        if type(receipt["exit_code"]) is not int or receipt["exit_code"] not in {0, 1} or receipt["error"] is not None:
            return reject("infra_error_or_invalid_exit")
        if (receipt["exit_code"] == 0) != receipt["resolved"]:
            return reject("exit_outcome_mismatch")
        # The adapter must normalize test failure to 1; pytest exit 2/3/4/5 are not unresolved repairs.
        for prefix in ("test_log", "raw_patch", "patch", "harness_patch"):
            blob = read_artifact(root, receipt[prefix + "_path"])
            if prefix == "test_log" and not blob.strip():
                return reject("empty_test_log")
            if prefix == "patch" and receipt["resolved"] and not blob.strip():
                return reject("empty_patch_cannot_claim_repair")
            if sha256(blob) != receipt[prefix + "_sha256"]:
                return reject("artifact_sha_mismatch:" + prefix)
        if receipt["patch_sha256"] != receipt["harness_patch_sha256"]:
            return reject("delivered_harness_patch_mismatch")
        if not isinstance(trusted_ledger, dict) or trusted_ledger.get("schema") != LEDGER_SCHEMA:
            return reject("no_independent_controller_ledger")
        expected_evaluator = trusted_ledger.get("evaluators", {}).get(receipt["evaluator_id"])
        if not isinstance(expected_evaluator, dict):
            return reject("untrusted_evaluator")
        for field in ("evaluator_version", "evaluator_sha256", "evaluator_kind", "source", "evidence_kind"):
            if expected_evaluator.get(field) != receipt[field]:
                return reject("evaluator_pin_mismatch:" + field)
        key = identity_key(x)
        binding = trusted_ledger.get("bindings", {}).get(key)
        if not isinstance(binding, dict):
            return reject("no_independent_run_binding")
        for field in BIND_FIELDS:
            if type(binding.get(field)) is not type(receipt[field]) or binding.get(field) != receipt[field]:
                return reject("controller_binding_mismatch:" + field)
        if binding.get("receipt_sha256") != digest:
            return reject("controller_receipt_sha_mismatch")
        replay_keys = {("identity", key), ("evaluation_id", receipt["evaluation_id"]), ("receipt", digest)}
        if seen is not None:
            if seen & replay_keys:
                return reject("replayed_evaluation")
            seen.update(replay_keys)
        return {"state": "EVALUATED", "resolved": receipt["resolved"],
                "evidence_kind": receipt["evidence_kind"], "reason": "CONTENT_AND_CONTROLLER_BOUND"}
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return reject("malformed_or_missing_evidence")


def verify_experiment_csv(csv_path: Path, receipt_root: Path, trusted_ledger: dict | None) -> dict:
    seen, results, outcomes = set(), [], defaultdict(lambda: defaultdict(list))
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            return {"state": "UNVERIFIED", "reason": "missing_or_duplicate_csv_columns", "rows": []}
        for row in reader:
            result = validate_receipt(row, receipt_root, trusted_ledger, seen)
            results.append({**{k: row.get(k) for k in IDENTITY}, **result})
            if result["state"] == "EVALUATED":
                outcomes[row["arm"]][row["task_id"]].append(int(result["resolved"]))
    valid = bool(results) and all(r["state"] == "EVALUATED" for r in results)
    kinds = {r.get("evidence_kind") for r in results}
    # No success-rate aggregation if any row is invalid or synthetic/real evidence is mixed.
    summaries = {}
    if valid and len(kinds) == 1:
        for arm, tasks in outcomes.items():
            summaries[arm] = {"independent_tasks": len(tasks), "evaluations": sum(map(len, tasks.values())),
                              "task_mean_resolved": sum(sum(v) / len(v) for v in tasks.values()) / len(tasks)}
    return {"state": "EVALUATED" if summaries else "UNVERIFIED", "rows": results, "arms": summaries,
            "evidence_kind": next(iter(kinds)) if len(kinds) == 1 else "MIXED_OR_MISSING",
            "inference": "DESCRIPTIVE_ONLY_NO_SIGNIFICANCE_OR_OFFICIAL_SCORE_CLAIM"}


def load_trusted_ledger(path: Path, expected_sha256: str, receipt_root: Path) -> dict:
    path = path.resolve(strict=True)
    if path.is_relative_to(receipt_root.resolve()):
        raise ValueError("controller ledger must be outside Agent evidence root")
    raw = path.read_bytes()
    if sha256(raw) != expected_sha256:
        raise ValueError("controller ledger pin mismatch")
    return strict_json(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_csv", type=Path)
    parser.add_argument("--receipt-root", required=True, type=Path)
    parser.add_argument("--trusted-ledger", type=Path)
    parser.add_argument("--trusted-ledger-sha256")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    ledger = None
    if bool(args.trusted_ledger) != bool(args.trusted_ledger_sha256):
        parser.error("ledger and externally pinned SHA256 must be supplied together")
    if args.trusted_ledger:
        ledger = load_trusted_ledger(args.trusted_ledger, args.trusted_ledger_sha256, args.receipt_root)
    result = verify_experiment_csv(args.results_csv, args.receipt_root, ledger)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({"state": result["state"], "rows": len(result["rows"])}))
    return 0 if result["state"] == "EVALUATED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
