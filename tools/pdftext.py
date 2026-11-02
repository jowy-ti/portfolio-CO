"""Extract text from the course PDFs without any PDF library.

Usage:
    pixi run python tools/pdftext.py TOML2026_27_MLE_COP_Portfolio.pdf > /tmp/portfolio.txt

Why this exists: this environment has no `pdftotext` and no PDF library
(`pypdf`, `pdfminer`, PyMuPDF), and AGENTS.md forbids adding one. The course
PDFs keep their text in Flate-compressed content streams built from `Tj` / `TJ`
operators, so zlib plus a small parser is enough to read statements and
references.

Caveats: the output is de-spaced (`p(yj )` for $p(y\\mid\\theta)$) and maths is
approximate. Use it to find the exercise statements and the `[MLE x.y]` /
`[CO x]` references, not to typeset formulas. The `read` tool cannot open PDFs
for this model ("this model does not support pdf input"), so this script is the
only way in.
"""

from __future__ import annotations

import re
import sys
import zlib

_ESCAPES = {0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12, 0x28: 40, 0x29: 41, 0x5C: 92}


def _unescape(buf: bytes) -> str:
    """Decode a PDF literal string (backslash escapes and octal codes)."""
    out = bytearray()
    i = 0
    while i < len(buf):
        c = buf[i]
        if c == 0x5C and i + 1 < len(buf):
            nxt = buf[i + 1]
            if nxt in _ESCAPES:
                out.append(_ESCAPES[nxt])
                i += 2
                continue
            if 0x30 <= nxt <= 0x37:
                digits = b""
                j = i + 1
                while j < len(buf) and len(digits) < 3 and 0x30 <= buf[j] <= 0x37:
                    digits += bytes([buf[j]])
                    j += 1
                out.append(int(digits, 8) & 0xFF)
                i = j
                continue
            i += 2
            continue
        out.append(c)
        i += 1
    return bytes(out).decode("latin-1")


def extract_pages(path: str) -> list[str]:
    """Return the text of every content stream that draws text, in file order."""
    data = open(path, "rb").read()
    pages = []
    for stream in re.findall(rb"stream\r?\n(.*?)endstream", data, re.S):
        try:
            content = zlib.decompress(stream)
        except zlib.error:
            continue
        if b"TJ" not in content and b"Tj" not in content:
            continue
        lines, current = [], []
        for m in re.finditer(rb"\[(.*?)\]\s*TJ|\((.*?)\)\s*Tj|(Td|TD|T\*|BT|ET)", content, re.S):
            if m.group(1) is not None:                       # [ (a) -12 (b) ] TJ
                current.append("".join(_unescape(x) for x in
                                       re.findall(rb"\((.*?)(?<!\\)\)", m.group(1), re.S)))
            elif m.group(2) is not None:                     # (text) Tj
                current.append(_unescape(m.group(2)))
            elif m.group(3) in (b"Td", b"TD", b"T*", b"ET"):
                if current:
                    lines.append("".join(current))
                    current = []
        if current:
            lines.append("".join(current))
        pages.append("\n".join(lines))
    return pages


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.split("Caveats")[0].strip(), file=sys.stderr)
        return 2
    for i, page in enumerate(extract_pages(argv[1])):
        print(f"\n===== STREAM {i} =====")
        print(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
