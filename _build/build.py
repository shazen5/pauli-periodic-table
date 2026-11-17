"""Build index.html from _build/template.html and the notebook in assets/.

All notebook text (markdown cells), code cells and printed outputs are copied
straight from the .ipynb, so the website text is word for word the group's text.

Usage (from the repository folder):   python _build/build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = json.loads((ROOT / "assets" / "Topic8_Pauli_Periodic_Table.ipynb").read_text(encoding="utf-8"))
CELLS = NB["cells"]
TEMPLATE = (ROOT / "_build" / "template.html").read_text(encoding="utf-8")


def src(i):
    return "".join(CELLS[i]["source"])


# ---------- tiny Markdown renderer (only what the notebook uses) ----------
def math(tex):
    for a, b in [(r"\tfrac{1}{2}", "½"), (r"\,", " "), (r"\hbar", "ħ"),
                 (r"\omega", "ω"), (r"\dots", "…")]:
        tex = tex.replace(a, b)
    tex = html.escape(tex, quote=False)
    tex = re.sub(r"_(\w)", r"<sub>\1</sub>", tex)
    return f'<span class="math">{tex}</span>'


def inline(s):
    parts = re.split(r"(\$[^$]+\$)", s)
    out = []
    for p in parts:
        if p.startswith("$") and p.endswith("$") and len(p) > 1:
            out.append(math(p[1:-1]))
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r"`([^`]+)`", r"<code>\1</code>", p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", p)
        p = re.sub(r"(https?://[^\s)<]+)",
                   r'<a href="\1" target="_blank" rel="noopener">\1</a>', p)
        out.append(p)
    return "".join(out)


def markdown(text):
    lines = text.split("\n")
    out, para, i = [], [], 0

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            flush(); i += 1; continue
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            flush()
            tag = "h3" if len(m.group(1)) <= 2 else "h4"
            out.append(f'<{tag} class="nb-h">{inline(m.group(2))}</{tag}>')
            i += 1; continue
        if line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r"-+", c) for c in r)]
            t = ['<div class="tbl-wrap"><table class="nb-table"><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in body:
                t.append("<tr>" + "".join(
                    f'<td data-label="{html.escape(h)}">{inline(c) if c else "&nbsp;"}</td>'
                    for h, c in zip(head, r)) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t)); continue
        if re.match(r"^(- |\d+\. )", line):
            flush()
            ordered = bool(re.match(r"^\d+\. ", line))
            items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i].rstrip()))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        para.append(line.strip()); i += 1
    flush()
    return "\n".join(out)


def stream_out(i):
    texts = ["".join(o["text"]) for o in CELLS[i].get("outputs", []) if "text" in o]
    return "".join(texts).rstrip("\n")


def code_block(i):
    code = src(i)
    title = code.split("\n", 1)[0].lstrip("# ").strip()
    out = stream_out(i)
    out_html = (f'<div class="nb-out-label">Output</div><pre class="nb-out">{html.escape(out)}</pre>'
                if out else "")
    return (f'<details class="nb-code"><summary>Notebook code · {html.escape(title)}</summary>'
            f'<pre><code>{html.escape(code)}</code></pre>{out_html}</details>')


def render(m):
    kind, arg = m.group(1), m.group(2)
    if kind == "MD":
        return f'<div class="nb-text">{markdown(src(int(arg)))}</div>'
    if kind == "MDFROM":
        cell, marker = arg.split(":", 1)
        text = src(int(cell))
        return f'<div class="nb-text">{markdown(text[text.index(marker):])}</div>'
    if kind == "MEMBERS":
        line = next(l for l in src(0).split("\n") if l.startswith("**Group members:**"))
        return html.escape(line.replace("**Group members:**", "").strip())
    if kind == "CODE":
        return code_block(int(arg))
    if kind == "OUT":
        return f'<pre class="nb-out">{html.escape(stream_out(int(arg)))}</pre>'
    raise ValueError(kind)


page = re.sub(r"<!--(MDFROM|MD|MEMBERS|CODE|OUT):?([^>]*?)-->", render, TEMPLATE)
(ROOT / "index.html").write_text(page, encoding="utf-8")
print("index.html written,", len(page), "characters")
