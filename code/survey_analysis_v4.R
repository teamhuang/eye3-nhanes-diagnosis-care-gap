Sys.setenv(OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1)
suppressMessages(library(survey)); options(survey.lonely.psu="adjust"); set.seed(20261029)
CSV <- "C:/eye3/data/processed/analytic_dataset_v2.csv"; TBL <- "C:/eye3/results/tables"
d <- read.csv(CSV)

# ---- CORRECTED OUTCOME DEFINITIONS (responders only; missing self-report = NA) ----
# diagnosis-discordance = objectively graded disease AND the self-report item was ANSWERED
d$y_dr  <- ifelse(is.na(d$dx_dr), NA, ifelse(d$dx_dr==1, 0, 1))   # 1 = graded DR, no reported dx
d$y_amd <- ifelse(is.na(d$dx_amd), NA, ifelse(d$dx_amd==1, 0, 1)) # 1 = graded AMD, no reported dx
d$y_late<- ifelse(is.na(d$dx_amd), NA, ifelse(d$dx_amd==1, 0, 1))
# late-AMD subtype flags (worse eye): geographic atrophy vs exudative/neovascular
d$amd_ga  <- ifelse(d$obj_amd_late==1 & d$OPDUGA==1,1,ifelse(d$obj_amd_late==1,0,NA))
d$amd_nv  <- ifelse(d$obj_amd_late==1 & d$OPDUEXU==1,1,ifelse(d$obj_amd_late==1,0,NA))
d$educ_cat<- factor(d$educ, levels=c(1,2,3), labels=c("<HS","HS/GED",">HS"))
d$educ_bw <- factor(ifelse(d$educ==1,"<HS", ifelse(d$educ %in% c(2,3),"HS-or-more", NA)), levels=c("HS-or-more","<HS"))
d$race_bw <- factor(ifelse(d$RIDRETH1==3,"White","Non-White"), levels=c("White","Non-White"))
d$sex     <- factor(ifelse(d$male==1,"Male","Female"), levels=c("Female","Male"))
d$insured_f<-factor(ifelse(d$insured==1,"Insured","Uninsured"), levels=c("Insured","Uninsured"))
d$agec<-ifelse(d$age>=85,85,d$age); d$pir2<-d$pir; d$modplus<-ifelse(d$OPDURL4>=3,1,ifelse(!is.na(d$OPDURL4),0,NA))
des <- svydesign(ids=~SDMVPSU, strata=~SDMVSTRA, weights=~w_pooled, data=d, nest=TRUE)
SUB <- function(cond) subset(des, eval(parse(text=cond)))
Wp <- function(s,var){ r<-svyciprop(as.formula(paste0("~",var)),s,method="logit",na.rm=TRUE); ci<-confint(r); c(100*as.numeric(r),100*ci[1],100*ci[2]) }
Rw <- function(m,n,cond,var){w<-Wp(SUB(cond),var);data.frame(measure=m,n=n,est=w[1],lo=w[2],hi=w[3])}

cat("#### ASSERT responders-only denominators vs Python truth ####\n")
DRcond <- "dm_dx==1 & obj_dr_any==1 & !is.na(dx_dr)"
AMDcond<- "obj_amd_any==1 & !is.na(dx_amd)"
LTcond <- "obj_amd_late==1 & !is.na(dx_amd)"
ndr<-nrow(SUB(DRcond)$variables); namd<-nrow(SUB(AMDcond)$variables); nlt<-nrow(SUB(LTcond)$variables)
cat("DR responders:",ndr," AMD:",namd," Late:",nlt,"\n")
stopifnot(ndr==313, namd==436, nlt==55)

fit <- function(s, var, desc, rhs){
  g <- svyglm(as.formula(paste0(var," ~ ",rhs)), design=s, family=quasibinomial()); sm<-summary(g)
  dfres <- max(1, degf(s) - g$rank + 1); tc <- qt(0.975, dfres)
  cf<-rownames(sm$coefficients); cf<-cf[cf!="(Intercept)"]
  data.frame(model=desc, term=cf, aOR=exp(sm$coefficients[cf,1]),
             lo=exp(sm$coefficients[cf,1]-tc*sm$coefficients[cf,2]),
             hi=exp(sm$coefficients[cf,1]+tc*sm$coefficients[cf,2]),
             p_raw=sm$coefficients[cf,4], n=nrow(s$variables), df_resid=dfres)
}

# ================= 1. MISSINGNESS + MODEL-N RECONCILIATION (DR + AMD) =================
dr<-d[which(d$dm_dx==1 & d$obj_dr_any==1 & !is.na(d$dx_dr)),]
amd<-d[which(d$obj_amd_any==1 & !is.na(d$dx_amd)),]
miss_df<-data.frame(cohort=c(rep("DR-eligible (responders)",5),rep("AMD-eligible (responders)",5)),
  variable=rep(c("education(valid 1/2/3)","family income(PIR)","insurance","usual source of care","dilated-exam item(DIQ360)"),2),
  n_missing=c(sum(!dr$educ %in% c(1,2,3)), sum(is.na(dr$pir)), sum(is.na(dr$insured)), sum(is.na(dr$usual_src_private)), sum(is.na(dr$recent_dilated_exam)),
              sum(!amd$educ %in% c(1,2,3)), sum(is.na(amd$pir)), sum(is.na(amd$insured)), sum(is.na(amd$usual_src_private)), sum(is.na(amd$recent_dilated_exam))))
write.csv(miss_df, file.path(TBL,"t_missingness_v4.csv"), row.names=FALSE)
modeln<-data.frame(quantity=c("descriptive diagnosis-gap denominator (responders)",
  "CORE complete-case (educ AND income complete)","CORE + insurance (educ,income,insurance complete)",
  "missing-indicator SENSITIVITY (retains all responders; income median-filled + income&education missingness flags)",
  "education-complete subset [descriptive count ONLY, not a fitted model]",
  "AMD descriptive denominator (responders)","AMD CORE (educ+income complete)","AMD insurance-descriptive (insured known)"),
  n=c(ndr, sum(dr$educ %in% c(1,2,3)&!is.na(dr$pir)), sum(dr$educ %in% c(1,2,3)&!is.na(dr$pir)&!is.na(dr$insured)),
      ndr, sum(dr$educ %in% c(1,2,3)),
      namd, sum(amd$educ %in% c(1,2,3)&!is.na(amd$pir)), sum(amd$educ %in% c(1,2,3)&!is.na(amd$pir)&!is.na(amd$insured))))
write.csv(modeln, file.path(TBL,"t_modeln_v4.csv"), row.names=FALSE); print(modeln,row.names=FALSE)

# ================= 2. PREVALENCE (self-report items are asked of all -> unchanged) =================
prev<-rbind(
 Rw("Any objectively graded retinopathy (all 40+, descriptive)",5704,"!is.na(OPDUARMA)","obj_dr_any"),
 Rw("Moderate-or-worse retinopathy (all 40+)",5704,"!is.na(OPDUARMA)","obj_dr_modsev"),
 Rw("Objective retinopathy AMONG adults with diabetes",884,"dm_dx==1 & !is.na(OPDUARMA)","obj_dr_any"),
 Rw("Any AMD (early+late)",5604,"!is.na(OPDUARM)","obj_amd_any"),
 Rw("Late AMD",5604,"!is.na(OPDUARM)","obj_amd_late"),
 Rw("Diagnosed diabetes",6639,"!is.na(dm_dx)","dm_dx"),
 Rw("Insured (any coverage)",6788,"!is.na(insured)","insured"),
 Rw("Self-reported glaucoma dx",6760,"!is.na(dx_glau)","dx_glau"),
 Rw("Self-reported cataract operation",6790,"!is.na(dx_cataract_op)","dx_cataract_op"))
write.csv(prev, file.path(TBL,"t_prevalence_v4.csv"), row.names=FALSE); print(prev,row.names=FALSE,digits=3)

# ================= 3. GAPS (responders only) =================
# care gap = 100 - %examined (recent_dilated_exam==1 means examined within 12 months)
gap<-rbind(
 Rw("DR: graded retinopathy in diabetes, NO self-reported dx",ndr,DRcond,"y_dr"),
 Rw("AMD: graded AMD, NO self-reported dx",namd,AMDcond,"y_amd"),
 Rw("Late AMD: graded late AMD, NO self-reported dx",nlt,LTcond,"y_late"))
care_dm  <- SUB("dm_dx==1 & !is.na(recent_dilated_exam)")
care_dr  <- SUB("dm_dx==1 & obj_dr_any==1 & !is.na(dx_dr) & !is.na(recent_dilated_exam)")
wc_dm<-Wp(care_dm,"recent_dilated_exam"); wc_dr<-Wp(care_dr,"recent_dilated_exam")
gap<-rbind(gap,
 data.frame(measure="Care: NO dilated exam within 12 months (all diabetes)", n=nrow(care_dm$variables), est=100-wc_dm[1], lo=100-wc_dm[3], hi=100-wc_dm[2]),
 data.frame(measure="Care: NO dilated exam within 12 months (diabetes + retinopathy)", n=nrow(care_dr$variables), est=100-wc_dr[1], lo=100-wc_dr[3], hi=100-wc_dr[2]))
write.csv(gap, file.path(TBL,"t_gaps_v4.csv"), row.names=FALSE); print(gap,row.names=FALSE,digits=3)

# ================= 4. CORE + INSURANCE LOGISTIC =================
CORE<-"agec + sex + educ_bw + race_bw + pir2"
s_dr<-SUB(paste(DRcond,"& !is.na(educ_bw) & !is.na(pir2)")); s_amd<-SUB(paste(AMDcond,"& !is.na(educ_bw) & !is.na(pir2)"))
mod<-rbind(fit(s_dr,"y_dr","PRIMARY: no-reported-dx DR",CORE), fit(s_amd,"y_amd","PRIMARY: no-reported-dx AMD",CORE))
mod$p_holm<-NA; for(m in unique(mod$model)){i<-which(mod$model==m); mod$p_holm[i]<-p.adjust(mod$p_raw[i],"holm")}
write.csv(mod, file.path(TBL,"t_logistic_primary_v4.csv"), row.names=FALSE); print(mod,row.names=FALSE,digits=3)

s_dri<-SUB(paste(DRcond,"& !is.na(educ_bw) & !is.na(pir2) & !is.na(insured_f)"))
ins_dr<-fit(s_dri,"y_dr","SUPP: DR + insurance", paste(CORE,"+ insured_f")); write.csv(ins_dr,file.path(TBL,"t_logistic_insurance_DR_v4.csv"),row.names=FALSE)
ai<-SUB(paste(AMDcond,"& !is.na(educ_bw) & !is.na(pir2) & !is.na(insured_f)")); vv<-ai$variables
amd_ins<-data.frame(known_insured_n=nrow(vv), insured_n=sum(vv$insured==1), insured_undiag=sum(vv$insured==1&vv$y_amd==1),
                    uninsured_n=sum(vv$insured==0), uninsured_undiag=sum(vv$insured==0&vv$y_amd==1))
write.csv(amd_ins,file.path(TBL,"t_insurance_AMD_descriptive_v4.csv"),row.names=FALSE); print(amd_ins)

# ---- missing-indicator SENSITIVITY model (retains all 313 responders; income median-filled + flags) ----
d$pir_missing<-ifelse(is.na(d$pir),1,0)
d$pir_filled <-ifelse(is.na(d$pir), median(d$pir,na.rm=TRUE), d$pir)
d$educ_missing<-ifelse(!d$educ %in% c(1,2,3),1,0)
d$educ_bw2   <-factor(ifelse(d$educ==1,"low", ifelse(d$educ %in% c(2,3),"high","high")), levels=c("high","low"))
des$variables<-d   # refresh design data frame with the new derived columns
s_mi<-SUB(paste(DRcond))
mi_tab<-fit(s_mi,"y_dr","MI-full (retains all responders; educ_bw2 + pir_filled + missingness flags)",
            "agec + sex + educ_bw2 + race_bw + pir_filled + factor(pir_missing) + factor(educ_missing)")
write.csv(mi_tab,file.path(TBL,"t_sensitivityC_v4.csv"),row.names=FALSE)
cat("\n-- MI-full sensitivity model n =",nrow(s_mi$variables),"--\n"); print(mi_tab,row.names=FALSE,digits=3)

# ================= 5. UNIFIED SEVERITY TABLE (fixes 197/203) =================
rows<-list(); for(lv in c(1,2,3,4)){
  s<-SUB(paste0("dm_dx==1 & OPDURL4==",lv," & !is.na(dx_dr)")); nn<-nrow(s$variables); w<-Wp(s,"y_dr")
  rows[[length(rows)+1]]<-data.frame(OPDURL4=lv, n_responders=nn, pct_reported_dx=100-w[1], gap_pct_undiagnosed=w[1], lo=w[2], hi=w[3])
}
sev<-do.call(rbind,rows); write.csv(sev,file.path(TBL,"t_severity_unified_v4.csv"),row.names=FALSE)
cat("\n-- unified severity (diabetics, responders, by OPDURL4) --\n"); print(sev,row.names=FALSE,digits=3)
cat("sum responders:", sum(sev$n_responders), "\n")

# age-stratified gaps (AMD & DR) on responders
agevars<-list("AMD 40-59"=c(AMDcond,"agec<60","y_amd"),"AMD 60-74"=c(AMDcond,"agec>=60 & agec<75","y_amd"),
  "AMD >=75"=c(AMDcond,"agec>=75","y_amd"),"AMD >=50"=c(AMDcond,"agec>=50","y_amd"),
  "DR 40-59"=c(DRcond,"agec<60","y_dr"),"DR 60-74"=c(DRcond,"agec>=60 & agec<75","y_dr"),"DR >=75"=c(DRcond,"agec>=75","y_dr"))
ag<-do.call(rbind,lapply(names(agevars),function(k){v<-agevars[[k]];s<-SUB(paste0(v[1]," & ",v[2]));w<-Wp(s,v[3]);
  data.frame(stratum=k,n=nrow(s$variables),est=w[1],lo=w[2],hi=w[3])}))
write.csv(ag,file.path(TBL,"t_agestrata_v4.csv"),row.names=FALSE); cat("\n-- age strata --\n"); print(ag,row.names=FALSE,digits=3)

# ================= 6. ANALYSIS A =================
cat("\n#### ANALYSIS A ####\n")
sA<-SUB(paste(DRcond,"& !is.na(recent_dilated_exam)"))
crude_list<-lapply(c(0,1),function(g){
  sg<-subset(sA, eval(parse(text=paste0("recent_dilated_exam==",g))))
  r<-svyciprop(~y_dr, sg, method="logit", na.rm=TRUE); cii<-confint(r)
  data.frame(recent_dilated_exam=g, y_dr=as.numeric(r), lo=cii[1], hi=cii[2], unweighted_n=nrow(sg$variables))
})
crude<-do.call(rbind,crude_list); write.csv(crude,file.path(TBL,"tA_crude_v4.csv"),row.names=FALSE)
cat("-- crude (0=not examined<=12mo,1=examined; logit CI) --\n"); print(crude,row.names=FALSE,digits=3)
sB<-SUB(paste(DRcond,"& !is.na(recent_dilated_exam) & !is.na(educ_bw) & !is.na(pir2) & !is.na(insured_f)"))
adjA<-fit(sB,"y_dr","ANALYSIS A adjusted (all covariates)","recent_dilated_exam + agec + sex + educ_bw + race_bw + pir2 + insured_f + factor(OPDURL4)")
adjA$p_holm<-p.adjust(adjA$p_raw,"holm"); write.csv(adjA,file.path(TBL,"tA_adjusted_v4.csv"),row.names=FALSE)
cat("-- adjusted n =",nrow(sB$variables),"--\n"); print(adjA,row.names=FALSE,digits=3)
# g-computation: marginal probability of NO reported dx under exam=0 vs exam=1, + RD (cluster bootstrap CI)
gcomp_rd <- function(dd){
  f<-svyglm(y_dr~recent_dilated_exam+agec+sex+educ_bw+race_bw+pir2+insured_f+factor(OPDURL4), design=dd, family=quasibinomial())
  d0<-dd$variables; d0$recent_dilated_exam<-0; d1<-dd$variables; d1$recent_dilated_exam<-1
  p0<-predict(f,newdata=d0,type="response"); p1<-predict(f,newdata=d1,type="response"); w<-dd$variables$w_pooled
  c(m0=weighted.mean(p0,w), m1=weighted.mean(p1,w), RD=weighted.mean(p1,w)-weighted.mean(p0,w))
}
gpt<-gcomp_rd(sB)
set.seed(20261029)
gb<-tryCatch(survey::bootstrap(sB, gcomp_rd(sB), times=200), error=function(e){cat("boot err:",conditionMessage(e),"\n");NULL})
gci<-tryCatch({ if(is.null(gb)) stop("no boot"); m<-as.matrix(gb); if(ncol(m)!=3||all(is.na(m))) stop("degenerate");
   q<-apply(m,2,function(v)quantile(v,c(.025,.975),na.rm=TRUE)); if(any(is.na(q))) stop("NA-CI"); q },
   error=function(e){cat("bootstrap CI not reliable (sparse PSU):",conditionMessage(e),"-- reporting point estimate only\n");NULL})
cat("\n-- g-computation marginal risk --\n"); print(gpt,digits=3)
if(!is.null(gci)) print(t(gci),digits=3)
lo_v<-if(is.null(gci)) c(NA,NA,NA) else c(gci[1,"m0"],gci[1,"m1"],gci[1,"RD"])
hi_v<-if(is.null(gci)) c(NA,NA,NA) else c(gci[2,"m0"],gci[2,"m1"],gci[2,"RD"])
gcom_out<-data.frame(quantity=c("marginal P(no dx | exam=0)","marginal P(no dx | exam=1)","risk difference (exam1-exam0)"),
                     est=c(unname(gpt["m0"]),unname(gpt["m1"]),unname(gpt["RD"])), lo=lo_v, hi=hi_v, ci_available=!is.null(gci))
write.csv(gcom_out,file.path(TBL,"tA_gcom_v4.csv"),row.names=FALSE)
sI<-SUB(paste(DRcond,"& !is.na(recent_dilated_exam) & !is.na(educ_bw) & !is.na(pir2) & !is.na(insured_f) & !is.na(modplus)"))
fI<-svyglm(y_dr~recent_dilated_exam*modplus + agec+sex+educ_bw+race_bw+pir2+insured_f, design=sI, family=quasibinomial())
smI<-summary(fI); ci<-grep(":", rownames(smI$coefficients), value=TRUE)
it<-smI$coefficients[ci,]
dfI<-max(1, degf(sI)-fI$rank+1); tcI<-qt(0.975,dfI)
int_tab<-data.frame(term=ci, aOR=exp(it[1]), lo=exp(it[1]-tcI*it[2]), hi=exp(it[1]+tcI*it[2]), p=it[4], n=nrow(sI$variables))
write.csv(int_tab,file.path(TBL,"tA_interaction_v4.csv"),row.names=FALSE); cat("\n-- interaction (exam x modplus) --\n"); print(int_tab,row.names=FALSE,digits=3)

# ================= 7. LATE AMD SUBTYPE (GA vs neovascular) =================
cat("\n#### LATE AMD SUBTYPE ####\n")
ga<-SUB("obj_amd_late==1 & OPDUGA==1 & !is.na(dx_amd)"); nv<-SUB("obj_amd_late==1 & OPDUEXU==1 & !is.na(dx_amd)")
wg<-Wp(ga,"y_late"); wn<-Wp(nv,"y_late")
sub<-rbind(data.frame(subtype="Geographic atrophy", n=nrow(ga$variables), est=wg[1], lo=wg[2], hi=wg[3]),
           data.frame(subtype="Exudative/neovascular", n=nrow(nv$variables), est=wn[1], lo=wn[2], hi=wn[3]))
write.csv(sub,file.path(TBL,"t_lateAMD_subtype_v4.csv"),row.names=FALSE); print(sub,row.names=FALSE,digits=3)

# ================= 8. NHIS AGE-STANDARDISATION DETAIL =================
nhis<-read.csv("C:/eye3/data/processed/nhis_adult_2016_eye40plus.csv")
nhis$md<-as.numeric(ifelse(nhis$eye_mac %in% c(0,1),nhis$eye_mac,NA))
bands<-function(a) cut(a,breaks=c(40,50,60,70,80,200),labels=c("40-49","50-59","60-69","70-79","80+"),right=FALSE,include.lowest=TRUE)
nhis$band<-factor(bands(nhis$age40plus_num),levels=c("40-49","50-59","60-69","70-79","80+"))
ndes<-svydesign(ids=~psu,strata=~strata,weights=~wt,data=nhis,nest=TRUE)
d$band<-factor(bands(d$age),levels=c("40-49","50-59","60-69","70-79","80+"))
for(lv in levels(d$band)) d[[paste0("bd_",make.names(lv))]]<-as.integer(d$band==lv)
bdcols<-paste0("bd_",make.names(levels(d$band))); desB<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
bp<-as.vector(svymean(as.formula(paste("~",paste(bdcols,collapse="+"))),desB)); names(bp)<-levels(d$band); std_w<-bp/sum(bp)
rates<-as.data.frame(svyby(~md,~band,ndes,svymean,na.rm=TRUE)); colnames(rates)[2:3]<-c("rate","se"); rates$band<-as.character(rates$band)
rates$standard_weight_NHANES<-as.numeric(std_w)[match(rates$band,names(std_w))]; rates$weighted_contribution<-rates$rate*rates$standard_weight_NHANES
mmd<-svymean(~md,ndes,na.rm=TRUE); cc<-confint(mmd); cw<-coef(mmd)["md"]; cl<-as.numeric(cc[1]); ch<-as.numeric(cc[2])
ok<-!is.na(rates$rate); se_<-sum(rates$rate[ok]*rates$standard_weight_NHANES[ok])/sum(rates$standard_weight_NHANES[ok])
sese<-sqrt(sum((rates$standard_weight_NHANES[ok]*rates$se[ok])^2))/sum(rates$standard_weight_NHANES[ok])
write.csv(rates,file.path(TBL,"t_nhis_std_detail_v4.csv"),row.names=FALSE); print(rates,row.names=FALSE,digits=4)
nhis_std<-data.frame(quantity=c("NHIS 2016 self-reported macular degeneration, survey-weighted crude (>=40)",
  "NHIS age-standardised to NHANES 2005-2008 40+ structure (5 bands)"),
  est_pct=c(100*cw,100*se_), lo_pct=c(100*cl,100*(se_-1.96*sese)), hi_pct=c(100*ch,100*(se_+1.96*sese)))
write.csv(nhis_std,file.path(TBL,"t_nhis_weighted_std_v4.csv"),row.names=FALSE)
cat(sprintf("\nNHIS crude weighted=%.4f (%.4f-%.4f); age-standardised=%.4f (%.4f-%.4f)\n",
 100*cw,100*cl,100*ch,100*se_,100*(se_-1.96*sese),100*(se_+1.96*sese)))
cat("\n== Done survey_analysis_v4 ==\n")
