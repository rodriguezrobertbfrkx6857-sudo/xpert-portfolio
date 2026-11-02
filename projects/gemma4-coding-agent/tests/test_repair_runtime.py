"""在临时 Git 仓库检验实际写入、失败恢复及交付审计，不使用模型假成功标签。"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

MODULE = Path(__file__).resolve().parents[1] / "repair_runtime.py"
spec = importlib.util.spec_from_file_location("g11_repair_runtime", MODULE)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def git(root, *args):
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_COUNT="0", GIT_TERMINAL_PROMPT="0")
    return subprocess.run(["git", "-c", "user.name=G11 Test", "-c", "user.email=g11@example.invalid", *args],
                          cwd=root, env=env, check=True, capture_output=True).stdout


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    files = {"pkg/a.py": b"def value():\n    return 1\n",
             "pkg/b.py": b"def other():\n    return 2\n",
             "pkg/nested/tests/test_a.py": b"assert True\n",
             "pkg/nested/conftest.py": b"value = 1\n",
             "pkg/nested/pyproject.toml": b"[tool.pytest]\n",
             "pkg/dup.py": b"a = 1\nb = 1\n",
             "pkg/crlf.py": b"def value():\r\n    return 1\r\n",
             "pkg/caller.py": b"from .a import value\n\nprint(value())\n",
             "pkg/binary.py": b"abc\x00def",
             ".gitignore": b"ignored.py\n"}
    for name, body in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    git(root, "init", "-q")
    git(root, "add", ".")
    git(root, "commit", "-qm", "fixture")
    return root


def edit(root, path="pkg/a.py", old="return 1", new="return 3", **kwargs):
    value = dict(path=path, old=old, new=new, sha256=runtime.digest((root/path).read_bytes()))
    value.update(kwargs)
    return value


def invoke(repo, action, **kwargs):
    return runtime.run(dict(action=action, **kwargs), repo)


def test_multi_file_edit_and_audit(repo):
    result = invoke(repo, "edit", edits=[edit(repo), edit(repo, "pkg/b.py", "return 2", "return 4")])
    assert result["ok"] and result["status"] == "EDITED"
    assert (repo/"pkg/a.py").read_text().endswith("return 3\n")
    assert (repo/"pkg/b.py").read_text().endswith("return 4\n")
    audit = invoke(repo, "audit")
    assert audit["raw_tracked_patch_nonempty"]
    assert audit["changed_tracked"] == ["pkg/a.py", "pkg/b.py"]
    assert not audit["requires_review"]
    assert "resolved" not in audit
    assert audit["test_result"] == "NOT_RUN"


def test_second_file_syntax_failure_keeps_first_pristine(repo):
    before = (repo/"pkg/a.py").read_bytes()
    result = invoke(repo, "edit", edits=[edit(repo), edit(repo, "pkg/b.py", "return 2", "return (")])
    assert result["status"] == "SYNTAX_ERROR"
    assert (repo/"pkg/a.py").read_bytes() == before
    assert git(repo, "diff") == b""


def test_stale_second_file_prevents_all_edits(repo):
    result = invoke(repo, "edit", edits=[edit(repo), edit(repo, "pkg/b.py", "return 2", "return 4", sha256="0"*64)])
    assert result["status"] == "STALE_SOURCE"
    assert git(repo, "diff") == b""


def test_ambiguous_old_rejected(repo):
    result = invoke(repo, "edit", edits=[edit(repo, "pkg/dup.py", "= 1", "= 3")])
    assert result["status"] == "NON_UNIQUE_MATCH"
    assert git(repo, "diff") == b""


def test_overlapping_literal_match_rejected(repo):
    (repo/"pkg/a.py").write_text('value = "aaa"\n')
    result = invoke(repo, "edit", edits=[edit(repo, old="aa", new="bb")])
    assert result["status"] == "NON_UNIQUE_MATCH"


def test_multiple_nonoverlapping_same_file_edits(repo):
    result = invoke(repo, "edit", edits=[edit(repo, old="def value", new="def better"), edit(repo)])
    assert result["ok"]
    assert (repo/"pkg/a.py").read_text() == "def better():\n    return 3\n"


def test_overlapping_edit_intervals_rejected(repo):
    result = invoke(repo, "edit", edits=[edit(repo), edit(repo, old="    return 1", new="    return 4")])
    assert result["status"] == "OVERLAPPING_EDIT"


def test_crlf_preserved_and_lf_model_text_accepted(repo):
    result = invoke(repo, "edit", edits=[edit(repo, "pkg/crlf.py", "def value():\n    return 1", "def value():\n    return 3")])
    assert result["ok"]
    assert (repo/"pkg/crlf.py").read_bytes() == b"def value():\r\n    return 3\r\n"


@pytest.mark.parametrize("name", ["pkg/nested/tests/test_a.py", "pkg/nested/conftest.py", "pkg/nested/pyproject.toml"])
def test_nested_protected_files_rejected(repo, name):
    result = invoke(repo, "edit", edits=[edit(repo, name, "1", "2")])
    assert result["status"] == "PROTECTED_PATH"
    assert git(repo, "diff") == b""


@pytest.mark.parametrize("name", ["pkg/sitecustomize.py", "pkg/usercustomize.py", "pkg/_swegemma_stubs.py", "pkg/testing/helpers.py"])
def test_official_harness_protected_runtime_files_rejected(repo, name):
    target = repo/name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('value = 1\n')
    git(repo, 'add', name)
    result = invoke(repo, "edit", edits=[edit(repo, name, "1", "2")])
    assert result["status"] == "PROTECTED_PATH"
    assert target.read_text() == 'value = 1\n'


@pytest.mark.parametrize("name", ["../escape.py", "/tmp/file.py", "pkg/../pkg/a.py", "pkg\\a.py", ".git/config", "C:/file.py", "pkg//a.py"])
def test_path_traversal_and_metadata_rejected(repo, name):
    request = dict(path=name, sha256="0"*64, old="a", new="b")
    result = invoke(repo, "edit", edits=[request])
    assert result["status"] == "UNSAFE_PATH"


def test_untracked_edit_rejected(repo):
    (repo/"new.py").write_text("value = 1\n")
    assert invoke(repo, "edit", edits=[edit(repo, "new.py", "1", "2")])["status"] == "UNTRACKED_EDIT"


def test_binary_rejected(repo):
    request = dict(path="pkg/binary.py", sha256="0"*64, old="abc", new="xyz")
    assert invoke(repo, "edit", edits=[request])["status"] == "BINARY_OR_LARGE"


def test_symlink_rejected(repo):
    target = repo/"pkg/link.py"
    try:
        target.symlink_to(repo/"pkg/a.py")
    except OSError:
        pytest.skip("当前账户无创建符号链接权限")
    git(repo, "add", "pkg/link.py")
    result = invoke(repo, "edit", edits=[edit(repo, "pkg/link.py", "return 1", "return 3")])
    assert result["status"] == "SYMLINK"


def test_parent_symlink_gate_without_platform_privilege(repo, monkeypatch):
    original = Path.is_symlink

    def simulated_parent(path):
        return True if path == repo/"pkg" else original(path)

    monkeypatch.setattr(Path, "is_symlink", simulated_parent)
    result = invoke(repo, "edit", edits=[edit(repo)])
    assert result["status"] == "SYMLINK"
    assert git(repo, "diff") == b""


def test_write_failure_restores_all_original_bytes(repo, monkeypatch):
    original = Path.write_bytes
    failed = False

    def fail_second_once(path, data):
        nonlocal failed
        if path.name == "b.py" and not failed:
            failed = True
            original(path, b"partial write")
            raise OSError("injected disk failure")
        return original(path, data)

    monkeypatch.setattr(Path, "write_bytes", fail_second_once)
    result = invoke(repo, "edit", edits=[edit(repo), edit(repo, "pkg/b.py", "return 2", "return 4")])
    assert result["status"] == "WRITE_ROLLED_BACK"
    assert git(repo, "diff") == b""


def test_persistent_write_failure_reports_manual_recovery(repo, monkeypatch):
    original = Path.write_bytes

    def fail_second_persistently(path, data):
        if path.name == "b.py":
            original(path, b"partial write")
            raise OSError("injected persistent failure")
        return original(path, data)

    monkeypatch.setattr(Path, "write_bytes", fail_second_persistently)
    result = invoke(repo, "edit", edits=[edit(repo), edit(repo, "pkg/b.py", "return 2", "return 4")])
    assert result["status"] == "ROLLBACK_FAILED" and not result["ok"]
    assert "pkg/b.py" in result["error"]
    assert (repo/"pkg/a.py").read_bytes() == b"def value():\n    return 1\n"


def test_precommit_recheck_detects_concurrent_change(repo, monkeypatch):
    original = runtime.Runtime.read
    calls = 0

    def changed_on_second_read(self, name, writable=False):
        nonlocal calls
        calls += 1
        if calls == 2:
            (repo/"pkg/a.py").write_text("external = 4\n")
        return original(self, name, writable)

    monkeypatch.setattr(runtime.Runtime, "read", changed_on_second_read)
    result = invoke(repo, "edit", edits=[edit(repo)])
    assert result["status"] == "STALE_SOURCE"
    assert (repo/"pkg/a.py").read_text() == "external = 4\n"


def test_audit_reports_untracked_ignored_and_runtime_temp(repo):
    (repo/"new.py").write_text("value = 3\n")
    (repo/"scratch.json").write_text("{}")
    (repo/".adk_exec_deadbeef.py").write_text("pass\n")
    (repo/"ignored.py").write_text("value = 3\n")
    result = invoke(repo, "audit")
    assert result["requires_review"]
    assert "new.py" in result["untracked"]
    assert result["runtime_temporary"] == [".adk_exec_deadbeef.py"]
    assert result["ignored_count"] == 1
    assert {x["path"] for x in result["unsafe_paths"]} == {"scratch.json"}


def test_audit_detects_rename_into_test_directory(repo):
    git(repo, "mv", "pkg/a.py", "pkg/nested/tests/new.py")
    result = invoke(repo, "audit")
    assert "pkg/a.py" in result["changed_tracked"]
    assert any(x["path"] == "pkg/nested/tests/new.py" for x in result["unsafe_paths"])


def test_locate_ranks_exact_path_returns_hash_and_caller(repo):
    result = invoke(repo, "locate", symbols=["value"], paths=["pkg/a.py"])
    assert result["ok"] and result["matches"][0]["path"] == "pkg/a.py"
    assert result["matches"][0]["sha256"] == runtime.digest((repo/"pkg/a.py").read_bytes())
    assert any(x["path"] == "pkg/caller.py" for x in result["matches"])
    assert len(result["matches"]) <= 5
    assert len(json.dumps(result).encode()) <= runtime.MAX_OUTPUT_BYTES


def test_locate_literal_not_regex(repo):
    result = invoke(repo, "locate", symbols=[".*"])
    assert result["status"] == "NO_MATCH"


@pytest.mark.parametrize("payload", [{}, {"action": []}, {"action": "locate"}, {"action": "edit", "edits": []},
                                    {"action": "locate", "symbols": [""]}, {"action": "locate", "paths": ["a"], "max_results": 100},
                                    {"action": "audit", "time_budget_seconds": 100}, []])
def test_malformed_request_fails_closed(repo, payload):
    result = runtime.run(payload, repo)
    assert result["ok"] is False


def test_cli_valid_and_invalid_request(repo):
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    good = subprocess.run([sys.executable, str(MODULE), "--root", str(repo), "--request", '{"action":"audit"}'], capture_output=True, text=True, encoding='utf-8', env=env)
    assert good.returncode == 0 and json.loads(good.stdout)["status"] == "AUDITED"
    bad = subprocess.run([sys.executable, str(MODULE), "--root", str(repo), "--request", '{}'], capture_output=True, text=True, encoding='utf-8', env=env)
    assert bad.returncode == 2 and json.loads(bad.stdout)["ok"] is False
    assert "Traceback" not in bad.stderr


def test_helper_deadline_is_enforced(repo):
    result = invoke(repo, "audit", time_budget_seconds=.000001)
    assert result["status"] == "TIME_BUDGET"


def test_hardlink_outside_repo_rejected(repo):
    # Same filesystem: a tracked path may share an inode with an outside file.
    target = repo / "pkg/a.py"
    outside = repo.parent / "outside_hardlinked.py"
    original = target.read_bytes()
    outside.write_bytes(original)
    target.unlink()
    try:
        os.link(outside, target)
    except (OSError, NotImplementedError):
        pytest.skip("hardlinks unavailable on this filesystem")
    outcome = invoke(repo, "edit", edits=[edit(repo)])
    assert outcome["status"] == "HARDLINK"
    assert outside.read_bytes() == original
    assert target.read_bytes() == original
