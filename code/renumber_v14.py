"""Round-14 renumbering after Methods-before-Results reorder.
Single-pass regex (no chain corruption). Refs renumbered by first appearance in the NEW order;
supplementary tables renumbered likewise; reference list physically reordered."""
from pathlib import Path
import re
from docx import Document

ROOT=Path("C:/eye3/manuscript/eye3")
D=ROOT/"manuscript"/"题目3手稿最新版本.docx"
d=Document(str(D)); ps=d.paragraphs

SUP="⁰¹²³⁴⁵⁶⁷⁸⁹"; DIG="0123456789"
def to_int(s): return int(s.translate(str.maketrans(SUP,DIG)))
def to_sup(n): return "".join(SUP[int(c)] for c in str(n))

CLUST=re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+(?:[,\u207b\u2013][⁰¹²³⁴⁵⁶⁷⁸⁹]+)*")
def expand_cluster(c):
    toks=re.split(r"([,\u207b\u2013])", c)
    nums=[to_int(t) for t in toks if t and t not in ",\u207b\u2013"]
    seps=[t for t in toks if t in ",\u207b\u2013"]
    out=[nums[0]]
    for k,sep in enumerate(seps):
        nx=nums[k+1]
        if sep in ("\u207b","\u2013"): out.extend(range(out[-1]+1,nx+1))
        else: out.append(nx)
    return out

def is_citer(p):
    t=p.text
    return bool(re.search(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]",t)) and not any(
        k in t for k in ("Huang","Wang","University","Corresponding","Department","Eye Institute"))

# --- compute REFMAP from CURRENT (post-reorder) first-appearance order ---
ref_order=[]
for p in ps:
    if not (5 < ps.index(p) < 95) or not is_citer(p): continue
    for c in CLUST.findall(p.text):
        for n in expand_cluster(c):
            if n not in ref_order: ref_order.append(n)
REFMAP={old:i+1 for i,old in enumerate(ref_order)}

# --- compute SPTMAP from supplementary-table first-appearance order ---
sp_order=[]
for p in ps:
    for m in re.findall(r"Supplementary Table S(\d+)", p.text):
        n=int(m)
        if n not in sp_order: sp_order.append(n)
SPTMAP={old:i+1 for i,old in enumerate(sp_order)}
print("ref appearance:",ref_order,"\nSPTMAP:",SPTMAP,"\nREFMAP:",REFMAP)

def renum_cluster(m):
    vals=expand_cluster(m.group(0))
    new=sorted({REFMAP[v] for v in vals})
    return ",".join(to_sup(n) for n in new)

# cite-paragraphs: contain citation superscripts, in body (5..94), not author/affiliation lines
def is_citer(p):
    t=p.text
    return bool(re.search(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]",t)) and 5<ps.index(p)<95 and not any(
        k in t for k in ("Huang","Wang","University","Corresponding","Department","Eye Institute"))
citers=[]
for p in ps:
    if is_citer(p):
        citers.append(ps.index(p))
        for r in p.runs:
            new=CLUST.sub(renum_cluster, r.text)
            if new!=r.text: r.text=new

# supplementary-table renumber (main text + captions), single pass, only "Supplementary Table S<n>"
for p in ps:
    for r in p.runs:
        if "Supplementary Table S" in r.text:
            r.text=re.sub(r"(Supplementary Table S)(\d)",
                          lambda mm:f"{mm.group(1)}{SPTMAP.get(int(mm.group(2)),int(mm.group(2)))}", r.text)

# physically reorder the reference list to the new numbering
ref_head=next(i for i,p in enumerate(ps) if p.text.strip()=="References")
ref_head_el=ps[ref_head]._p
ref_paras=[p for p in ps[ref_head+1:] if p.text.strip()]
assert len(ref_paras)==16, f"expected 16 refs got {len(ref_paras)}"
by_old={k+1:ref_paras[k]._p for k in range(16)}
inv={v:k for k,v in REFMAP.items()}          # new -> old
for p in ref_paras: p._p.getparent().remove(p._p)
cur=ref_head_el
for newnum in range(1,17):
    el=by_old[inv[newnum]]
    cur.addnext(el); cur=el

d.save(str(D))
print("citers renumbered:",citers)
print("saved")
