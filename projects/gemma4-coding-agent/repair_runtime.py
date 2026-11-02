"""G11 有界检索、乐观锁编辑及交付审计；只使用 Python 标准库。

该工具不调用模型、不判定 resolved，也不控制官方 Agent 的全局调用预算。
CLI: python repair_runtime.py --root /workspace --request '{"action":"audit"}'
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time

VERSION = "g11-runtime-1"
SOURCE_EXTENSIONS = {".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".scala", ".kt", ".swift", ".sh", ".vue", ".svelte"}
MAX_FILE_BYTES = 524288
MAX_REQUEST_BYTES = 1048576
MAX_SCAN_BYTES = 16 * 1024 * 1024
MAX_OUTPUT_BYTES = 24000


class RepairError(Exception):
    """可供模型纠正的有限失败类别。"""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def digest(data):
    return hashlib.sha256(data).hexdigest()


def protected(name):
    """所有嵌套目录均应用保护规则，而非只检查根目录。"""
    parts = PurePosixPath(name).parts
    lower = [p.lower() for p in parts]
    base = lower[-1] if lower else ""
    return (any(p in {"test", "tests", "testing", "__tests__", ".git", ".github", ".hg", ".svn"} for p in lower)
            or base.startswith("test_") or base.endswith("_test.py")
            or ".test." in base or ".spec." in base
            or base in {"conftest.py", "pytest.ini", ".pytest.ini", "tox.ini", "pyproject.toml", "setup.cfg", "setup.py", ".gitignore", ".gitattributes", "noxfile.py", "jest.config.js", "vitest.config.ts", "sitecustomize.py", "usercustomize.py", "_swegemma_stubs.py"}
            or base.startswith("requirements"))


class Runtime:
    def __init__(self, root, seconds=10.0):
        self.started = time.monotonic()
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not 0 < seconds <= 15:
            raise RepairError("INVALID_BUDGET", "time_budget_seconds 必须在 (0,15] 内")
        self.deadline = self.started + seconds
        self.root = Path(root).absolute()
        if self.root.is_symlink() or self.root.resolve() != self.root:
            raise RepairError("UNSAFE_ROOT", "root 不得通过符号链接定位")
        if not self.root.is_dir() or (self.root / ".git").is_symlink():
            raise RepairError("UNSAFE_ROOT", "root 必须是普通 Git 工作目录")
        actual = self.git("rev-parse", "--show-toplevel").decode("utf-8").strip()
        if Path(actual).resolve() != self.root:
            raise RepairError("WRONG_ROOT", "root 必须是仓库根目录")
        self.files = self.git("ls-files", "-z").decode("utf-8").split("\0")
        self.files = sorted(set(p for p in self.files if p))
        self.tracked = set(self.files)

    def check_time(self):
        if time.monotonic() >= self.deadline:
            raise RepairError("TIME_BUDGET", "本次 helper 的时间预算已用完")

    def git(self, *args):
        self.check_time()
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        try:
            result = subprocess.run(["git", "-c", "core.quotePath=false", *args],
                                    cwd=self.root, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, timeout=max(.001, self.deadline-time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            raise RepairError("TIME_BUDGET", "Git 操作超时") from exc
        if result.returncode:
            raise RepairError("GIT_ERROR", result.stderr.decode("utf-8", "replace")[:600])
        return result.stdout

    def safe_path(self, name, writable=False):
        if not isinstance(name, str) or not name or "\\" in name or "\0" in name or ":" in name:
            raise RepairError("UNSAFE_PATH", "只允许仓库相对 POSIX 路径")
        p = PurePosixPath(name)
        if p.is_absolute() or any(x in {".", "..", ".git"} for x in p.parts) or str(p) != name:
            raise RepairError("UNSAFE_PATH", "拒绝绝对路径、路径穿越和 Git 元数据")
        candidate = self.root.joinpath(*p.parts)
        for parent in [candidate, *candidate.parents]:
            if parent == self.root:
                break
            if parent.is_symlink():
                raise RepairError("SYMLINK", "拒绝符号链接及其子路径")
        if not candidate.resolve().is_relative_to(self.root):
            raise RepairError("UNSAFE_PATH", "路径逃逸")
        if writable:
            if name not in self.tracked:
                raise RepairError("UNTRACKED_EDIT", "edit 只支持已跟踪文件；新增文件使用官方工具并审计")
            if protected(name) or p.suffix.lower() not in SOURCE_EXTENSIONS:
                raise RepairError("PROTECTED_PATH", "只能修改非测试、非配置的源文件")
        if not candidate.is_file():
            raise RepairError("MISSING_FILE", "路径不是普通文件")
        # Hard-linked inodes can escape repository confinement without symlinks.
        # Fail closed instead of writing through a shared inode.
        if writable and candidate.stat().st_nlink != 1:
            raise RepairError("HARDLINK", "拒绝多个硬链接共享的文件写入")
        return candidate

    def read(self, name, writable=False):
        self.check_time()
        target = self.safe_path(name, writable)
        if target.stat().st_size > MAX_FILE_BYTES:
            raise RepairError("FILE_TOO_LARGE", "文件超过 512 KiB")
        data = target.read_bytes()
        if len(data) > MAX_FILE_BYTES or b"\0" in data:
            raise RepairError("BINARY_OR_LARGE", "拒绝二进制或过大文件")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RepairError("ENCODING", "当前版本仅支持 UTF-8 源文件") from exc
        return data

    def locate(self, req):
        """固定字符串检索；搜索结果附原字节哈希以供后续编辑。"""
        symbols, paths = req.get("symbols", []), req.get("paths", [])
        for values in (symbols, paths):
            if not isinstance(values, list) or len(values) > 12 or any(not isinstance(s, str) or not s or len(s) > 128 for s in values):
                raise RepairError("INVALID_QUERY", "symbols/paths 为最多 12 个非空短字符串")
        if not symbols and not paths:
            raise RepairError("INVALID_QUERY", "必须给出 issue 中已知的符号或路径")
        limit = req.get("max_results", 5)
        if type(limit) is not int or not 1 <= limit <= 8:
            raise RepairError("INVALID_QUERY", "max_results 必须为 1..8")
        # 精确/后缀路径优先，避免大仓库扫描预算耗尽时遗漏已知文件。
        ordered = sorted(self.files, key=lambda p: (-int(any(p == x or p.endswith("/"+x) for x in paths)), p))
        hits, scanned, scan_bytes, skipped = [], 0, 0, 0
        truncated = False
        for name in ordered:
            if scanned >= 5000 or scan_bytes >= MAX_SCAN_BYTES or time.monotonic() >= self.deadline:
                truncated = True
                break
            if PurePosixPath(name).suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            scanned += 1
            try:
                data = self.read(name)
            except RepairError:
                skipped += 1
                continue
            scan_bytes += len(data)
            text = data.decode("utf-8")
            exact_path = any(name == x or name.endswith("/"+x) for x in paths)
            path_matches = sum(s in name for s in symbols)
            content_symbols = [s for s in symbols if s in text]
            if not exact_path and not path_matches and not content_symbols:
                continue
            lines = text.splitlines()
            line_matches = [i for i, line in enumerate(lines) if any(s in line for s in symbols)]
            # 声明优先；同名调用者仍作为其它候选返回，不声称构建完整调用图。
            definitions = [i for i in line_matches if re.match(r"\s*(?:async\s+)?(?:def|class|function|func)\s", lines[i])]
            index = (definitions or line_matches or [0])[0]
            lo, hi = max(0, index-5), min(len(lines), index+10)
            excerpt = "\n".join(f"{i+1}: {lines[i]}" for i in range(lo, hi))[:1700]
            score = 100*exact_path + 12*path_matches + 8*len(content_symbols) + 5*bool(definitions)
            hits.append({"path": name, "score": score, "sha256": digest(data),
                         "line": index+1, "protected": protected(name), "excerpt": excerpt,
                         "matched_symbols": content_symbols})
            hits.sort(key=lambda row: (-row["score"], row["path"]))
            hits = hits[:limit]
        return {"status": "LOCATED" if hits else "NO_MATCH", "matches": hits,
                "scanned_files": scanned, "scanned_bytes": scan_bytes, "skipped_files": skipped,
                "scan_truncated": truncated, "search_kind": "fixed_string_ranked"}

    def edit(self, req):
        """先完成全部预检，再修改；普通写入失败时恢复原字节。

        这是进程内回滚，并非跨文件崩溃原子事务，也不抵御并发恶意写入。
        """
        edits = req.get("edits")
        if not isinstance(edits, list) or not 1 <= len(edits) <= 16:
            raise RepairError("INVALID_EDIT", "edits 必须含 1..16 条修改")
        originals, plans, spans = {}, {}, {}
        for edit in edits:
            if not isinstance(edit, dict) or set(edit) != {"path", "sha256", "old", "new"}:
                raise RepairError("INVALID_EDIT", "每项必须且仅含 path/sha256/old/new")
            name, expected, old, new = (edit[k] for k in ("path", "sha256", "old", "new"))
            if not isinstance(name, str):
                raise RepairError("INVALID_EDIT", "path 必须是字符串")
            if not isinstance(old, str) or not old or not isinstance(new, str) or old == new:
                raise RepairError("INVALID_EDIT", "old 必须非空，且 new 必须产生修改")
            data = originals.setdefault(name, self.read(name, writable=True))
            if expected != digest(data):
                raise RepairError("STALE_SOURCE", "文件哈希与读取时不一致：" + name)
            old_b, new_b = old.encode("utf-8"), new.encode("utf-8")
            # CRLF 文件的模型 JSON 常使用 LF；只做一致的换行归一化，不模糊匹配。
            if b"\r\n" in data and b"\n" not in data.replace(b"\r\n", b""):
                old_b = old_b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                new_b = new_b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            if data.count(old_b) != 1 or data.find(old_b, data.find(old_b)+1) >= 0:
                raise RepairError("NON_UNIQUE_MATCH", "old 必须恰好出现一次：" + name)
            start = data.index(old_b)
            end = start+len(old_b)
            prior = spans.setdefault(name, [])
            if any(start < b and a < end for a, b, _ in prior):
                raise RepairError("OVERLAPPING_EDIT", "同文件替换区间不得重叠：" + name)
            prior.append((start, end, new_b))
        for name, data in originals.items():
            updated = data
            for start, end, new_b in sorted(spans[name], reverse=True):
                updated = updated[:start] + new_b + updated[end:]
            if len(updated) > MAX_FILE_BYTES or b"\0" in updated or updated == data:
                raise RepairError("INVALID_RESULT", "结果为空操作、二进制或过大：" + name)
            if name.endswith((".py", ".pyi")):
                try:
                    ast.parse(updated, filename=name)
                except (SyntaxError, ValueError) as exc:
                    raise RepairError("SYNTAX_ERROR", f"{name}: {exc}") from exc
            plans[name] = updated
        self.check_time()
        # 提交前对所有源文件再次检查，避免预检期间的正常并发修改被覆盖。
        for name, data in originals.items():
            if self.read(name, writable=True) != data:
                raise RepairError("STALE_SOURCE", "预检期间文件变化：" + name)
        attempted = []
        try:
            for name, updated in plans.items():
                self.check_time()
                target = self.safe_path(name, writable=True)
                if target.read_bytes() != originals[name]:
                    raise RepairError("STALE_SOURCE", "写入前文件变化：" + name)
                attempted.append(name)
                target.write_bytes(updated)
        except Exception as exc:
            failures = []
            for name in reversed(attempted):
                try:
                    self.safe_path(name, writable=True).write_bytes(originals[name])
                except Exception:
                    failures.append(name)
            if failures:
                raise RepairError("ROLLBACK_FAILED", "需人工恢复：" + ", ".join(failures)) from exc
            raise RepairError("WRITE_ROLLED_BACK", "写入失败，已恢复本事务原字节") from exc
        return {"status": "EDITED", "files": [{"path": p, "before_sha256": digest(originals[p]),
                 "after_sha256": digest(data)} for p, data in plans.items()],
                "syntax_checked": [p for p in plans if p.endswith((".py", ".pyi"))],
                "validation": "syntax_only_not_tests", "rollback_scope": "in_process_write_failure"}

    def audit(self, req):
        """原始 tracked diff 与未跟踪文件分列；不能冒充官方过滤后的补丁。"""
        raw = self.git("diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD", "--")
        # --no-renames 使移动的源/目标都接受保护检查。
        changed = self.git("diff", "--name-only", "--no-renames", "-z", "HEAD", "--").decode("utf-8").split("\0")
        untracked = self.git("ls-files", "--others", "--exclude-standard", "-z").decode("utf-8").split("\0")
        ignored = self.git("ls-files", "--others", "--ignored", "--exclude-standard", "-z").decode("utf-8").split("\0")
        changed, untracked, ignored = ([p for p in row if p] for row in (changed, untracked, ignored))
        runtime_temporary = [p for p in untracked if re.fullmatch(r"\.adk_exec_[0-9a-fA-F]{8}\.py", p)]
        unsafe = []
        for name in changed + untracked:
            if protected(name) or PurePosixPath(name).suffix.lower() not in SOURCE_EXTENSIONS:
                unsafe.append({"path": name, "reason": "protected_or_non_source"})
                continue
            try:
                if (self.root/name).exists() or (self.root/name).is_symlink():
                    self.safe_path(name)
            except RepairError as exc:
                unsafe.append({"path": name, "reason": exc.code})
        return {"status": "AUDITED", "raw_tracked_patch_sha256": digest(raw), "raw_tracked_patch_bytes": len(raw),
                "raw_tracked_patch_nonempty": bool(raw), "changed_tracked": changed[:80],
                "untracked": untracked[:80], "runtime_temporary": runtime_temporary[:80],
                "ignored_count": len(ignored), "unsafe_paths": unsafe[:80],
                "listing_truncated": max(len(changed), len(untracked), len(unsafe)) > 80,
                "requires_review": bool(untracked or unsafe or not raw),
                "patch_scope": "git_diff_HEAD_not_official_delivery", "test_result": "NOT_RUN"}


def run(request, root):
    started = time.monotonic()
    try:
        if not isinstance(request, dict):
            raise RepairError("INVALID_REQUEST", "请求必须是 JSON object")
        if len(json.dumps(request, ensure_ascii=False).encode()) > MAX_REQUEST_BYTES:
            raise RepairError("REQUEST_TOO_LARGE", "请求超过 1 MiB")
        action = request.get("action")
        if not isinstance(action, str) or action not in {"locate", "edit", "audit"}:
            raise RepairError("INVALID_ACTION", "action 必须为 locate/edit/audit")
        runtime = Runtime(root, request.get("time_budget_seconds", 10.0))
        result = getattr(runtime, action)(request)
        result.update(ok=True, version=VERSION, elapsed_seconds=round(time.monotonic()-started, 6))
    except RepairError as exc:
        result = {"ok": False, "status": exc.code, "error": str(exc), "version": VERSION,
                  "elapsed_seconds": round(time.monotonic()-started, 6)}
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        result = {"ok": False, "status": "RUNTIME_ERROR", "error": str(exc)[:600], "version": VERSION,
                  "elapsed_seconds": round(time.monotonic()-started, 6)}
    if len(json.dumps(result, ensure_ascii=False).encode()) > MAX_OUTPUT_BYTES:
        # 不在编辑成功后返回失败标记，以免诱发模型重复写入。
        result = {k: v for k, v in result.items() if k not in {"matches", "changed_tracked", "untracked", "unsafe_paths"}}
        result.update(output_truncated=True, requires_review=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--request", help="JSON 请求；省略时从 stdin 读取")
    args = parser.parse_args()
    try:
        raw = args.request if args.request is not None else sys.stdin.read(MAX_REQUEST_BYTES+1)
        if len(raw.encode()) > MAX_REQUEST_BYTES:
            raise ValueError("request too large")
        result = run(json.loads(raw), args.root)
    except (ValueError, OSError) as exc:
        result = {"ok": False, "status": "INVALID_REQUEST", "error": str(exc)[:600]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
