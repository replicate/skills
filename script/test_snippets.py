#!/usr/bin/env python
"""
Test all code snippets extracted from the skill markdown files.

Parses fenced code blocks from every .md file under skills/replicate/,
then runs each one in parallel (8 workers). Reports pass/fail per snippet.

Snippets starting with ``// worker.js`` or ``// workflow.js`` are run inside
a temporary Wrangler project (``wrangler dev``) and exercised via HTTP.

Usage:
    REPLICATE_API_TOKEN=... python script/test_snippets.py
    REPLICATE_API_TOKEN=... python script/test_snippets.py --syntax-only
    REPLICATE_API_TOKEN=... python script/test_snippets.py --include references/PREDICTIONS.md
    REPLICATE_API_TOKEN=... python script/test_snippets.py --exclude references/DEPLOYMENTS.md
"""

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT_DIR / "skills" / "replicate"
TEST_DIR = ROOT_DIR / "test"

DEFAULT_EXCLUDE = ["references/DEPLOYMENTS.md"]

PIPELINE_MARKERS: list[str] = []

NODE_MODULES_DIR = TEST_DIR / "node_modules"

MAX_WORKERS = 8
WRANGLER_CONCURRENCY = 1

_wrangler_semaphore = threading.Semaphore(WRANGLER_CONCURRENCY)


@dataclass
class Snippet:
    file: str
    index: int
    lang: str
    code: str
    line: int

    @property
    def label(self):
        return f"{self.file}:{self.line} [{self.lang} #{self.index}]"

    def is_pipeline_only(self):
        return any(m in self.code for m in PIPELINE_MARKERS)

    @property
    def wrangler_kind(self):
        first_line = self.code.split("\n", 1)[0].strip()
        if first_line == "// worker.js":
            return "worker"
        if first_line == "// workflow.js":
            return "workflow"
        return None


def read_wrangler_port(proc: subprocess.Popen, timeout: int = 60) -> int:
    """Read wrangler's stdout in a thread until we find 'Ready on http://...:PORT'."""
    result = {"port": None, "output": b""}
    ready_event = threading.Event()

    def reader():
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            result["output"] += line
            m = re.search(rb"Ready on http://localhost:(\d+)", line)
            if m:
                result["port"] = int(m.group(1))
                ready_event.set()
                break

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    if not ready_event.wait(timeout):
        raise RuntimeError(
            f"wrangler dev did not become ready within {timeout}s\n"
            + result["output"].decode(errors="replace")
        )
    return result["port"]


def extract_snippets(md_path: Path, relative: str) -> list[Snippet]:
    text = md_path.read_text()
    snippets = []
    pattern = re.compile(r"^```(\w+)\n(.*?)^```", re.MULTILINE | re.DOTALL)
    for i, m in enumerate(pattern.finditer(text)):
        lang = m.group(1)
        code = m.group(2)
        line = text[: m.start()].count("\n") + 1
        if lang in ("bash", "python", "javascript"):
            snippets.append(
                Snippet(file=relative, index=i, lang=lang, code=code, line=line)
            )
    return snippets


# ---------- plain snippet runners ----------


def check_python_syntax(snippet: Snippet):
    compile(snippet.code, snippet.label, "exec")


def run_python(snippet: Snippet) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(snippet.code)
        f.flush()
        try:
            return subprocess.run(
                ["uvx", "--python", "3.12", "--with", "replicate", "python", f.name],
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ},
            )
        finally:
            os.unlink(f.name)


def check_js_syntax(snippet: Snippet):
    with tempfile.NamedTemporaryFile(suffix=".mjs", mode="w", delete=False) as f:
        f.write(snippet.code)
        f.flush()
        try:
            result = subprocess.run(
                ["node", "--check", f.name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise SyntaxError(result.stderr.strip())
        finally:
            os.unlink(f.name)


def run_js(snippet: Snippet) -> subprocess.CompletedProcess:
    code = snippet.code
    wrapped = f"(async () => {{\n{code}\n}})().catch(e => {{ console.error(e); process.exit(1); }});\n"

    with tempfile.NamedTemporaryFile(
        suffix=".cjs", mode="w", delete=False, dir=str(NODE_MODULES_DIR.parent)
    ) as f:
        f.write(wrapped)
        f.flush()
        try:
            return subprocess.run(
                ["node", f.name],
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ},
                cwd=str(NODE_MODULES_DIR.parent),
            )
        finally:
            os.unlink(f.name)


def run_bash(snippet: Snippet) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-e", "-c", snippet.code],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ},
    )


# ---------- wrangler runner ----------


def extract_workflow_class_names(code: str) -> list[str]:
    return re.findall(r"export\s+class\s+(\w+)\s+extends\s+WorkflowEntrypoint", code)


def scaffold_wrangler_project(tmpdir: Path, snippet: Snippet):
    (tmpdir / "src").mkdir()
    (tmpdir / "src" / "index.js").write_text(snippet.code)

    (tmpdir / "package.json").write_text(
        json.dumps(
            {
                "name": "snippet-test",
                "private": True,
                "type": "module",
            }
        )
    )

    wrangler_config = {
        "name": "snippet-test",
        "main": "src/index.js",
        "compatibility_date": "2025-01-01",
        "compatibility_flags": ["nodejs_compat"],
    }

    if snippet.wrangler_kind == "workflow":
        class_names = extract_workflow_class_names(snippet.code)
        wrangler_config["workflows"] = [
            {
                "name": f"wf-{cls.lower()}",
                "binding": binding_name_for_class(cls, snippet.code),
                "class_name": cls,
            }
            for cls in class_names
        ]

    (tmpdir / "wrangler.jsonc").write_text(json.dumps(wrangler_config, indent=2))
    os.symlink(str(NODE_MODULES_DIR), str(tmpdir / "node_modules"))


def binding_name_for_class(class_name: str, code: str):
    for m in re.finditer(r"env\.(\w+)\.\w+\(", code):
        binding = m.group(1)
        if binding != "REPLICATE_API_TOKEN" and binding.isupper():
            return binding
    return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()


FIXTURES_DIR = TEST_DIR / "fixtures"
TEST_IMAGE = FIXTURES_DIR / "me.png"


def run_wrangler_snippet(snippet: Snippet):
    tmpdir = Path(tempfile.mkdtemp(prefix="wrangler-test-"))
    proc = None
    try:
        scaffold_wrangler_project(tmpdir, snippet)
        token = os.environ["REPLICATE_API_TOKEN"]

        proc = subprocess.Popen(
            [
                str(NODE_MODULES_DIR / ".bin" / "wrangler"),
                "dev",
                "--port=0",
                f"--var=REPLICATE_API_TOKEN:{token}",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(tmpdir),
            env={**os.environ, "WRANGLER_SEND_METRICS": "false"},
            start_new_session=True,
        )

        port = read_wrangler_port(proc)

        if snippet.wrangler_kind == "workflow":
            exercise_workflow(port)
        else:
            exercise_worker(port, snippet)

    finally:
        if proc and proc.poll() is None:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
        shutil.rmtree(tmpdir, ignore_errors=True)


def exercise_worker(port: int, snippet: Snippet):
    url = f"http://localhost:{port}/"

    # Workers that read the request body as binary expect a raw image POST.
    if "request.arrayBuffer()" in snippet.code or "request.blob()" in snippet.code:
        image_data = TEST_IMAGE.read_bytes()
        req = urllib.request.Request(
            url,
            data=image_data,
            method="POST",
            headers={"Content-Type": "image/png"},
        )
    else:
        req = urllib.request.Request(url, method="GET")

    try:
        resp = urllib.request.urlopen(req, timeout=120)
        status = resp.status
        body = resp.read().decode()
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode()
    if status >= 500:
        raise RuntimeError(f"Worker returned HTTP {status}: {body[:300]}")


def exercise_workflow(port: int):
    url = f"http://localhost:{port}/"
    req = urllib.request.Request(url, method="GET")
    resp = urllib.request.urlopen(req, timeout=120)
    status = resp.status
    if status != 200:
        body = resp.read().decode()
        raise RuntimeError(f"Workflow trigger returned HTTP {status}: {body[:300]}")


# ---------- setup ----------


def ensure_node_modules():
    pkg_json = TEST_DIR / "package.json"
    current = json.loads(pkg_json.read_text()) if pkg_json.exists() else {}
    deps = current.get("dependencies", {})
    needs_install = not NODE_MODULES_DIR.exists() or "wrangler" not in deps

    if needs_install:
        print("Installing npm packages (replicate + wrangler)...")
        pkg_json.write_text(
            json.dumps(
                {
                    "name": "test",
                    "private": True,
                    "type": "commonjs",
                    "dependencies": {
                        "replicate": "^1.4.0",
                        "wrangler": "^4.0.0",
                    },
                },
                indent=2,
            )
            + "\n"
        )
        subprocess.run(
            ["npm", "install", "--silent"],
            cwd=str(TEST_DIR),
            check=True,
            capture_output=True,
        )
    elif not NODE_MODULES_DIR.exists():
        print("Installing npm packages...")
        subprocess.run(
            ["npm", "install", "--silent"],
            cwd=str(TEST_DIR),
            check=True,
            capture_output=True,
        )


# ---------- run a single snippet (called from thread pool) ----------


def run_one(snippet: Snippet, syntax_only: bool) -> tuple[Snippet, str | None]:
    """Return (snippet, None) on success or (snippet, error_message) on failure."""
    if snippet.lang == "python":
        check_python_syntax(snippet)
    elif snippet.lang == "javascript" and not snippet.wrangler_kind:
        check_js_syntax(snippet)

    if syntax_only:
        return snippet, None

    if snippet.wrangler_kind:
        with _wrangler_semaphore:
            run_wrangler_snippet(snippet)
        return snippet, None

    if snippet.lang == "python":
        result = run_python(snippet)
    elif snippet.lang == "javascript":
        result = run_js(snippet)
    elif snippet.lang == "bash":
        result = run_bash(snippet)
    else:
        return snippet, None

    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        if len(err) > 500:
            err = err[:500] + "..."
        return snippet, f"exit {result.returncode}: {err}"

    return snippet, None


# ---------- main ----------


def main():
    parser = argparse.ArgumentParser(
        description="Test code snippets in skill markdown files"
    )
    parser.add_argument(
        "--syntax-only", action="store_true", help="Only check syntax, don't execute"
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Only test these files (relative to skill dir)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Skip these files (relative to skill dir)",
    )
    args = parser.parse_args()

    if not os.environ.get("REPLICATE_API_TOKEN"):
        print("REPLICATE_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    excludes = set(args.exclude or DEFAULT_EXCLUDE)

    md_files = sorted(SKILL_DIR.rglob("*.md"))
    all_snippets = []
    for md_path in md_files:
        relative = str(md_path.relative_to(SKILL_DIR))
        if args.include and relative not in args.include:
            continue
        if relative in excludes:
            continue
        all_snippets.extend(extract_snippets(md_path, relative))

    if not all_snippets:
        print("No snippets found!")
        sys.exit(1)

    if not args.syntax_only:
        ensure_node_modules()

    passed = []
    failed = []
    skipped = []

    # Separate pipeline-only snippets (skipped) from runnable ones
    runnable = []
    for snippet in all_snippets:
        if snippet.is_pipeline_only():
            skipped.append((snippet, "pipeline-only"))
            print(f"  SKIP {snippet.label} (pipeline-only)")
        else:
            runnable.append(snippet)

    print_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_to_snippet = {
            pool.submit(run_one, snippet, args.syntax_only): snippet
            for snippet in runnable
        }
        for future in as_completed(future_to_snippet):
            snippet = future_to_snippet[future]
            try:
                _, err = future.result()
            except Exception as e:
                err = str(e)

            with print_lock:
                if err is None:
                    passed.append(snippet)
                    suffix = " (syntax)" if args.syntax_only else ""
                    print(f"  OK   {snippet.label}{suffix}")
                else:
                    failed.append((snippet, err))
                    print(f"  FAIL {snippet.label}")
                    for line in err.split("\n")[:5]:
                        print(f"       {line}")

    print()
    print(
        f"Results: {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped"
    )

    if failed:
        print("\nFailed snippets:")
        for snippet, err in failed:
            print(f"  {snippet.label}")
            for line in err.split("\n")[:3]:
                print(f"    {line}")
        sys.exit(1)


if __name__ == "__main__":
    main()
