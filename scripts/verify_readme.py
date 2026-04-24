"""Build and verify README.md.

Two responsibilities, run back-to-back:

1. **Build.** Expand ``<!-- source: module:symbol -->`` markers by
   replacing the ``fenced python block that immediately follows with the
   live source of that symbol (via :func:`inspect.getsource`). This
   keeps the README in sync with the code — no stale paraphrases.

2. **Verify.** Collect the shared ``python`` setup block and every
   doctest-style ``text`` block (first line starts with ``>>> ``),
   exec the setup, run each query under ``redirect_stdout``, and diff
   against the expected output. Exits non-zero on mismatch.

Run as ``python scripts/verify_readme.py``. Writes the rebuilt README
back to disk.
"""

from __future__ import annotations

import importlib
import inspect
import io
import re
import sys
import textwrap
from contextlib import redirect_stdout
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"

SOURCE_MARKER = re.compile(
    r"(<!-- source: ([\w\.]+):(\w+) -->\n+```python\n)(.*?)(```)",
    re.DOTALL,
)
PY_FENCE = re.compile(r"```python\n(.*?)```", re.DOTALL)
TEXT_FENCE = re.compile(r"```text\n(.*?)```", re.DOTALL)


def inject_sources(text: str) -> str:
    """Replace each source-marker block with fresh ``inspect.getsource``."""

    def sub(m: re.Match) -> str:
        prefix, module, symbol, suffix = m.group(1, 2, 3, 5)
        mod = importlib.import_module(module)
        obj = getattr(mod, symbol)
        src = inspect.getsource(obj)
        return f"{prefix}{src}{suffix}"

    return SOURCE_MARKER.sub(sub, text)


def split_query(block: str) -> tuple[str, str] | None:
    lines = block.splitlines(keepends=True)
    if not lines or not lines[0].startswith(">>> "):
        return None
    code_lines = [lines[0][4:]]
    i = 1
    while i < len(lines) and lines[i].startswith("... "):
        code_lines.append(lines[i][4:])
        i += 1
    code = "".join(code_lines)
    expected = "".join(lines[i:])
    return code, expected


def verify(text: str) -> int:
    setup_blocks = PY_FENCE.findall(text)
    # Setup = every python block that isn't the source of a catalog function
    # (those are shown for display only and re-included via `import`).
    # Identify display-only blocks by their source markers.
    display_blocks = set()
    for m in SOURCE_MARKER.finditer(text):
        display_blocks.add(m.group(4))
    setup = "\n".join(b for b in setup_blocks if b not in display_blocks)
    if not setup:
        print("no setup python block found", file=sys.stderr)
        return 1

    queries = [q for b in TEXT_FENCE.findall(text) if (q := split_query(b))]
    if not queries:
        print("no doctest-style text blocks found", file=sys.stderr)
        return 1

    failed = 0
    for i, (code, expected) in enumerate(queries, 1):
        ns: dict = {}
        buf = io.StringIO()
        try:
            exec(setup, ns)
            with redirect_stdout(buf):
                exec(code, ns)
        except Exception as exc:
            print(f"[{i}] FAIL: exception: {exc!r}")
            print(textwrap.indent(code, "  "))
            failed += 1
            continue
        got = buf.getvalue()
        if got != expected:
            print(f"[{i}] FAIL: stdout mismatch")
            print("--- code ---")
            print(textwrap.indent(code, "  "), end="")
            print("--- expected ---")
            print(textwrap.indent(expected, "  "), end="")
            print("--- got ---")
            print(textwrap.indent(got, "  "), end="")
            failed += 1
        else:
            print(f"[{i}] ok")

    return 1 if failed else 0


def main() -> int:
    text = README.read_text()
    new_text = inject_sources(text)
    if new_text != text:
        README.write_text(new_text)
        print(f"wrote refreshed sources to {README}")
    return verify(new_text)


if __name__ == "__main__":
    raise SystemExit(main())
