# Convert the authoritative manuscript .docx into a faithful Markdown copy for the
# deposited repository, preserving paragraph/table/figure order. Body text stays plain
# (only section headings get ##, figure/table captions get **bold** like the docx).
import re
from pathlib import Path
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "manuscript" / "题目3手稿最新版本.docx"
DST = ROOT / "manuscript" / "题目3手稿.md"

d = Document(str(SRC))
body = d.element.body

HEAD = {"Abstract", "Introduction", "Methods", "Results", "Discussion",
        "Conclusions", "Conclusion", "Data availability", "Funding",
        "Author contributions", "Competing interests", "Acknowledgements", "References"}
FIGMAP = ["Fig1_flowchart", "Fig2_gradient_forest", "Fig3_eyecare_dots"]

# map each w:tbl element to its Table object by document order
tables_in_order = d.tables
tbl_pos = {}
ti = 0
for ch in body.iterchildren():
    if ch.tag == qn("w:tbl"):
        tbl_pos[id(ch)] = tables_in_order[ti]
        ti += 1

figidx = 0
out = []


def is_bold_caption(p):
    return bool(p.runs and p.runs[0].bold) and re.match(r"^\s*(Figure|Table)\s", p.text)


def emit_table(t):
    rows = [[c.text.replace("\n", " ").strip() for c in r.cells] for r in t.rows]
    if not rows:
        return
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |",
             "| " + " | ".join(["---"] * ncol) + " |"]
    for r in rows[1:]:
        lines.append("| " + " | ".join(r) + " |")
    out.append("\n" + "\n".join(lines) + "\n")


for ch in body.iterchildren():
    if ch.tag == qn("w:p"):
        p = Paragraph(ch, d)
        # image?
        if p._p.findall(".//" + qn("a:blip")):
            fn = FIGMAP[figidx] if figidx < len(FIGMAP) else f"figure_{figidx}"
            out.append(f"\n![Figure {figidx+1}](figures/{fn}.png)\n")
            figidx += 1
            continue
        t = p.text.strip()
        if not t:
            out.append("")
            continue
        if t in HEAD:
            out.append(f"## {t}")
            continue
        if is_bold_caption(p):
            out.append("**" + t + "**")
            continue
        out.append(t)
    elif ch.tag == qn("w:tbl"):
        emit_table(tbl_pos[id(ch)])

md = "\n".join(out)
# Rebuild cleanly: find the abstract heading and add '---' after its paragraph.
lines = md.split("\n")
res = []
i = 0
while i < len(lines):
    res.append(lines[i])
    if lines[i].strip() == "## Abstract":
        # next non-empty line is abstract body; capture it then append '---'
        i += 1
        while i < len(lines) and lines[i].strip() == "":
            res.append(lines[i]); i += 1
        if i < len(lines):
            res.append(lines[i])  # abstract body
            res.append("")
            res.append("---")
    i += 1
md = "\n".join(res)
# collapse >2 blank lines
md = re.sub(r"\n{3,}", "\n\n", md)
DST.write_text(md, encoding="utf-8")
print("wrote", DST, "chars", len(md), "figures embedded", figidx)
