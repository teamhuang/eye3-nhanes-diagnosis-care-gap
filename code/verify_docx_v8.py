#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_docx_v8.py — audit the final manuscript DOCX after the formatting/language pass.
Checks: (1) every headline/regression number retained vs numbers_v7.csv; (2) denominator
assertions from CNT keys AND a raw recount; (3) all figures/tables explicitly cited, sub-panel
level, in appearance order; (4) NO bold outside headings and NO bold in table cells; (5) no ** or
markdown artifacts; (6) abstract <=200 words; (7) AI disclosure present; (8) no fabricated DOI/ORCID."""
import os, re, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ.setdefault(v,"1")
from pathlib import Path
import docx
ROOT=Path(__file__).resolve().parents[1]
DOCX=ROOT/"manuscript"/"题目3手稿最新版本.docx"
NUMS=ROOT/"results"/"tables"/"numbers_v7.csv"
RAW=ROOT/"data"/"processed"/"analytic_dataset_v2.csv"
fails,oks=[],[]
def check(n,c,d=""): (oks if c else fails).append((n,bool(c),d))
src={}
for row in csv.reader(open(NUMS,encoding="utf-8")):
    if row and row[0]!="key": src[row[0]]=row[1] if len(row)>1 else ""
d=docx.Document(str(DOCX))
paras=d.paragraphs
text="\n".join(p.text for p in paras)
cells="\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
full=text+"\n"+cells
def nd(x): return re.sub(r"[\u2013\u2014-]","–",x)
fu=nd(full)

# (1) headline numbers
headline=["70.2% (63.8–75.9)","82.2% (77.3–86.2)","41.4% (25.3–59.6)","32.4% (25.9–39.7)",
 "53.4% (38.7–67.5)","9.75% (95% CI 8.79–10.80)","6.58% (5.65–7.66)","33.0% (29.3–37.0)",
 "87.9% (84.4–90.6)","2.45% (2.22–2.69)","(aOR 0.30, 0.10–0.92","1.34 (0.92–1.96","1.39 (0.96–2.00","1.46 (1.08–1.97","1.38 (1.02–1.87"]
for h in headline: check("headline: "+h, nd(h) in fu)

# (2) regression aOR(CI) from numbers_v7 must appear
reg_missing=[]
for k,v in src.items():
    if k.startswith(("prim|","insDR|","Aadj|")):
        if k.startswith("insDR|") and k not in ("insDR|pir2","insDR|insured_fUninsured"): continue
        if k.startswith("Aadj|") and k not in ("Aadj|recent_dilated_exam","Aadj|pir2","Aadj|factor(OPDURL4)3","Aadj|factor(OPDURL4)4"): continue
        m=re.search(r"(\d+\.\d+) \((\d+\.\d+)[–-](\d+\.\d+)\)", v)
        if m:
            disp=nd(f"{m.group(1)} ({m.group(2)}–{m.group(3)})")
            if disp not in fu: reg_missing.append((k,disp))
check("all displayed regression aOR(CI) retained", not reg_missing, str(reg_missing[:6]))

# (3) denominators
def num(t): return int(re.sub(r"\D","",t))
CNT={k.split("|",1)[1]:num(v) for k,v in src.items() if k.startswith("CNT|")}
for nm,val,key in [("DR gradable",319,"dr_gradable_disease"),("DR responders",313,"dr_gap_responders"),
 ("DR core",187,"dr_core_complete_cases"),("AMD gradable",441,"amd_gradable_disease"),
 ("AMD responders",436,"amd_gap_responders"),("AMD core",226,"amd_core_complete_cases")]:
    check(f"{nm}=={val}", CNT.get(key)==val, str(CNT.get(key)))
RD=list(csv.DictReader(open(RAW,encoding="utf-8-sig")))
def gv(r,k):
    x=r.get(k,"").strip()
    if x in ("","NA","NaN","nan"): return None
    try: return float(x)
    except: return x
rc=dict(dg=0,dr=0,dc=0,ag=0,ar=0,ac=0,mi=0,mo=0,se=0,ga=0,nv=0,lt=0)
for r in RD:
    dm=gv(r,"dm_dx");odra=gv(r,"obj_dr_any");oda=gv(r,"obj_amd_any");oamd=gv(r,"OPDUARM")
    dxdr=gv(r,"dx_dr");dxamd=gv(r,"dx_amd");l4=gv(r,"OPDURL4");ed=gv(r,"educ");pir=gv(r,"pir")
    comp=ed is not None and int(ed) in (1,2,3) and pir is not None
    if dm==1 and odra==1:
        rc["dg"]+=1
        if dxdr is not None:
            rc["dr"]+=1
            if comp: rc["dc"]+=1
            if l4==2:rc["mi"]+=1
            elif l4==3:rc["mo"]+=1
            elif l4==4:rc["se"]+=1
    if oda==1:
        rc["ag"]+=1
        if dxamd is not None:
            rc["ar"]+=1
            if comp: rc["ac"]+=1
    if oamd==2: rc["lt"]+=1
    if gv(r,"OPDUGA")==1: rc["ga"]+=1
    if gv(r,"OPDUEXU")==1: rc["nv"]+=1
check("raw recount 319/313/187",(rc["dg"],rc["dr"],rc["dc"])==(319,313,187),str((rc["dg"],rc["dr"],rc["dc"])))
check("raw recount 441/436/226",(rc["ag"],rc["ar"],rc["ac"])==(441,436,226),str((rc["ag"],rc["ar"],rc["ac"])))
check("raw severity 197+85+31=313",rc["mi"]+rc["mo"]+rc["se"]==313,f"{rc['mi']},{rc['mo']},{rc['se']}")
check("raw GA+NV==55",rc["ga"]+rc["nv"]==55 and rc["lt"]==55)

# (4) figure/table citations: present, sub-panel, in appearance order
def firstpos(pat):
    m=re.search(re.escape(pat),full); return m.start() if m else -1
req=["Figure 1","Figure 2, left panel","Figure 2, right panel","Figure 3","Figure S1","Figure S2",
     "Table 1","Table 2","Table 3","Table 4","Table 5","Supplementary Table S3"]
for p in req: check("cited: "+p, firstpos(p)>=0)
check("main figures numbered by appearance order", 0<=firstpos("Figure 1")<firstpos("Figure 2, left panel")<firstpos("Figure 3"))
check("tables numbered by appearance order", 0<=firstpos("Table 1")<firstpos("Table 2")<firstpos("Table 3")<firstpos("Table 4")<firstpos("Table 5"))
check("Fig2 sub-panel left before right", 0<=firstpos("Figure 2, left panel")<firstpos("Figure 2, right panel"))

# (5) formatting: bold allowed on headings, figure captions and table captions
CAPTION_PREFIX = re.compile(r'^\s*(?:Figure|Table|Supplementary\s+(?:Figure|Table))[\s\u00a0]', re.IGNORECASE)
body_bold=[]
for i,p in enumerate(paras):
    if p.style and p.style.name.startswith(("Heading","Title")): continue
    if CAPTION_PREFIX.match(p.text or ''): continue
    if any(r.bold for r in p.runs if r.text.strip()): body_bold.append(i)
check("no bold outside headings/captions", not body_bold, str(body_bold[:8]))
cell_bold=sum(1 for t in d.tables for row in t.rows for c in row.cells
              for p in c.paragraphs if any(r.bold for r in p.runs if r.text.strip()))
check("no bold in table cells", cell_bold==0, str(cell_bold))
check("no markdown ** artifacts", "**" not in full)
check("headings carry bold", all(any(r.bold for r in p.runs) for p in paras if p.style and p.style.name.startswith("Heading") and p.text.strip()))

# (6) abstract length
ab=""
for i,p in enumerate(paras):
    if p.style and p.style.name.startswith("Heading") and p.text.strip().lower()=="abstract":
        ab=paras[i+1].text; break
wc=len(re.findall(r"\S+",ab)); check(f"abstract<=200 (= {wc})", 0<wc<=200, str(wc))

# (7) AI disclosure + no fabrication
check("AI disclosure present","AI coding assistant (QoderWork)" in full and "ICMJE" in full)
check("no fabricated Zenodo DOI", not re.search(r"10\.\d{4,5}/zenodo\.\d+", full))
check("no fabricated ORCID", not re.search(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", full))

print("="*60); print(f"PASSED: {len(oks)}   FAILED: {len(fails)}"); print("="*60)
if fails:
    for n,c,dd in fails: print(f"  [FAIL] {n}: {dd}")
    raise SystemExit(1)
print("ALL DOCX CHECKS PASS")
