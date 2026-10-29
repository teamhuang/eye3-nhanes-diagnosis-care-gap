import os
from pathlib import Path
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[v]="1"
import pandas as pd, numpy as np, pyreadstat

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/"data"/"raw"; OUT = ROOT/"data"/"processed"
OUT.mkdir(parents=True, exist_ok=True)

RET=["SEQN","OPDURET","OPDUARMA","OPDURL4","OPDUARM","OPDULARM","OPDUGA","OPDUEXU","OPDUD125","OPDUHD","OPDUAGA"]
VIQ=["SEQN","VIQ071","VIQ090","VIQ310"]
DIQ=["SEQN","DIQ010","DIQ080","DIQ360"]
DEMO=["SEQN","RIAGENDR","RIDAGEYR","RIDRETH1","DMDEDUC2","INDFMPIR","WTMEC2YR","SDMVPSU","SDMVSTRA","RIDSTATR"]
HIQ=["SEQN","HIQ011"]; HUQ=["SEQN","HUQ030"]

def L(fn,cols): return pyreadstat.read_xport(str(RAW/fn), usecols=cols)[0]
def cyc(suf):
    m=L(f"OPXRET_{suf}.xpt",RET).merge(L(f"VIQ_{suf}.xpt",VIQ),on="SEQN",how="left",validate="1:1")
    m=m.merge(L(f"DIQ_{suf}.xpt",DIQ),on="SEQN",how="left",validate="1:1")
    m=m.merge(L(f"DEMO_{suf}.xpt",DEMO),on="SEQN",how="left",validate="1:1")
    m=m.merge(L(f"HUQ_{suf}.xpt",HUQ),on="SEQN",how="left",validate="1:1")
    m=m.merge(L(f"HIQ_{suf}.xpt",HIQ),on="SEQN",how="left",validate="1:1")
    m["cycle"]=suf; return m

def yn(s): return s.map({1:1,2:0})
def derive(df):
    df=df.copy()
    df["obj_dr_any"]=(df.OPDUARMA==1).astype(float); df.loc[df.OPDUARMA.isna(),"obj_dr_any"]=np.nan
    df["obj_dr_modsev"]=(df.OPDURL4>=3).astype(float); df.loc[df.OPDURL4.isna(),"obj_dr_modsev"]=np.nan
    df["obj_amd_any"]=(df.OPDUARM>=1).astype(float); df.loc[df.OPDUARM.isna(),"obj_amd_any"]=np.nan
    df["obj_amd_late"]=(df.OPDUARM==2).astype(float); df.loc[df.OPDUARM.isna(),"obj_amd_late"]=np.nan
    df["dx_dr"]=yn(df.DIQ080); df["dx_amd"]=yn(df.VIQ310); df["dx_glau"]=yn(df.VIQ090); df["dx_cataract_op"]=yn(df.VIQ071)
    df["dm_dx"]=yn(df.DIQ010)
    df["recent_dilated_exam"]=df.DIQ360.isin([1,2]).astype(float); df.loc[df.DIQ360.isna(),"recent_dilated_exam"]=np.nan
    for src,tgt in [("obj_dr_any","undiagnosed_dr"),("obj_amd_any","undiagnosed_amd"),("obj_amd_late","undiagnosed_amd_late")]:
        df[tgt]=np.nan; m=(df[src]==1); dx="dx_dr" if "dr" in tgt else "dx_amd"
        df.loc[m,tgt]=(df.loc[m,dx]!=1).astype(float)
    df["male"]=(df.RIAGENDR==1).astype(float); df["age"]=df.RIDAGEYR; df["pir"]=df.INDFMPIR; df["educ"]=df.DMDEDUC2
    df["insured"]=yn(df.HIQ011)                       # 1=covered, 0=not covered
    df["usual_src_private"]=(df.HUQ030==1).astype(float); df.loc[df.HUQ030.isna(),"usual_src_private"]=np.nan
    df["w_pooled"]=df.WTMEC2YR/2.0
    return df

df=pd.concat([derive(cyc("D")),derive(cyc("E"))],ignore_index=True)
df["pid"]=df.cycle.map({"D":0,"E":1})*10_000_000+df.SEQN
keep=["pid","cycle","SEQN","age","male","RIDRETH1","educ","pir","insured","usual_src_private",
      "SDMVPSU","SDMVSTRA","w_pooled","OPDUARMA","OPDURL4","OPDUARM","OPDUAGA","OPDUGA","OPDUEXU","OPDUD125",
      "obj_dr_any","obj_dr_modsev","obj_amd_any","obj_amd_late","dx_dr","dx_amd","dx_glau","dx_cataract_op",
      "dm_dx","recent_dilated_exam","undiagnosed_dr","undiagnosed_amd","undiagnosed_amd_late"]
df=df[[c for c in keep if c in df.columns]]
tmp=str(OUT/"analytic_dataset_v2.csv")+".tmp"; df.to_csv(tmp,index=False); os.replace(tmp,OUT/"analytic_dataset_v2.csv")
print("v2 rows",len(df),"insured nonmissing",df.insured.notna().sum(),"obj DR|dm",((df.dm_dx==1)&(df.obj_dr_any==1)).sum())
print("DR gap people",int(((df.dm_dx==1)&(df.obj_dr_any==1)&df.undiagnosed_dr.notna()).sum()))
print("missing among DR-gap candidates: educ",int(((df.dm_dx==1)&(df.obj_dr_any==1)&df.undiagnosed_dr.notna()&df.educ.isna()).sum()),
      "pir",int(((df.dm_dx==1)&(df.obj_dr_any==1)&df.undiagnosed_dr.notna()&df.pir.isna()).sum()),
      "insured",int(((df.dm_dx==1)&(df.obj_dr_any==1)&df.undiagnosed_dr.notna()&df.insured.isna()).sum()))
print("written analytic_dataset_v2.csv")
