Sys.setenv(OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1)
suppressMessages(library(survey)); options(survey.lonely.psu="adjust"); set.seed(20261029)
CSV<-"C:/eye3/data/processed/analytic_dataset_v2.csv"; TBL<-"C:/eye3/results/tables"
d<-read.csv(CSV)
d$y_dr<-ifelse(is.na(d$dx_dr),NA,ifelse(d$dx_dr==1,0,1))
d$y_amd<-ifelse(is.na(d$dx_amd),NA,ifelse(d$dx_amd==1,0,1))
d$educ_bw<-factor(ifelse(d$educ==1,"<HS",ifelse(d$educ %in% c(2,3),"HS-or-more",NA)),levels=c("HS-or-more","<HS"))
d$race_bw<-factor(ifelse(d$RIDRETH1==3,"White","Non-White"),levels=c("White","Non-White"))
d$sex<-factor(ifelse(d$male==1,"Male","Female"),levels=c("Female","Male"))
d$insured_f<-factor(ifelse(d$insured==1,"Insured","Uninsured"),levels=c("Insured","Uninsured"))
d$agec<-ifelse(d$age>=85,85,d$age); d$pir2<-d$pir; d$cycle_n<-ifelse(d$cycle=="E",1,0)
d$modplus<-ifelse(d$OPDURL4>=3,1,ifelse(!is.na(d$OPDURL4),0,NA))
d$dmflag<-ifelse(d$dm_dx==1,1,0)
d$amdstage<-factor(ifelse(d$OPDUARM==2,"late",ifelse(d$OPDUARM==1,"early",NA)),levels=c("early","late"))
d$ageband<-cut(d$age,breaks=c(40,60,70,Inf),labels=c("40-59","60-69","70+"),right=FALSE,include.lowest=TRUE)
des<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
SUB<-function(cond) subset(des, eval(parse(text=cond)))
Wp<-function(s,var){r<-svyciprop(as.formula(paste0("~",var)),s,method="logit",na.rm=TRUE);ci<-confint(r);c(100*as.numeric(r),100*ci[1],100*ci[2])}
DRcond<-"dm_dx==1 & obj_dr_any==1 & !is.na(dx_dr)"; AMDcond<-"obj_amd_any==1 & !is.na(dx_amd)"
CORE<-"agec + sex + educ_bw + race_bw + pir2"

# ============ 19. PER-MODEL AUDIT TABLE (design df, residual df, rank, coef/SE/CI/P/Holm) ============
cat("#### 19. MODEL AUDIT TABLE ####\n")
audit<-function(s,desc,rhs,holmsort=TRUE){
  g<-svyglm(as.formula(paste0("y ~ ",rhs)),design=s,family=quasibinomial()); sm<-summary(g)
  dsgn<-degf(s); rank<-g$rank; dfres<-max(1,dsgn-rank+1); tc<-qt(0.975,dfres)
  cf<-rownames(sm$coefficients); cf<-cf[cf!="(Intercept)"]
  b<-sm$coefficients[cf,1]; se<-sm$coefficients[cf,2]; p<-sm$coefficients[cf,4]
  ph<-if(holmsort) p.adjust(p,"holm") else rep(NA_real_,length(cf))
  # keep FULL-precision (7dp) estimates; all 2-dp display strings are single-rounded downstream
  # (never re-rounded from an intermediate 3-dp value -> avoids the 1.9649->1.965->1.97 double-round error)
  orv<-exp(b); lov<-exp(b-tc*se); hiv<-exp(b+tc*se)
  data.frame(model=desc, design_df=dsgn, rank=rank, residual_df=dfres, ci_multiplier=round(tc,4),
             term=cf, coef=round(b,7), SE=round(se,7), aOR=round(orv,7),
             lo=round(lov,7), hi=round(hiv,7),
             aOR_disp=sprintf("%.2f",orv), lo_disp=sprintf("%.2f",lov), hi_disp=sprintf("%.2f",hiv),
             p_raw=signif(p,6), p_holm=signif(ph,6),
             n=nrow(s$variables))
}
dr_core<-SUB(paste(DRcond,"& !is.na(educ_bw) & !is.na(pir2)")); dr_core$variables$y<-dr_core$variables$y_dr
amd_core<-SUB(paste(AMDcond,"& !is.na(educ_bw) & !is.na(pir2)")); amd_core$variables$y<-amd_core$variables$y_amd
dr_ins<-dr_core; dr_ins$variables$y<-dr_ins$variables$y_dr
Aa<-SUB(paste(DRcond,"& !is.na(recent_dilated_exam) & !is.na(educ_bw) & !is.na(pir2)")); Aa$variables$y<-Aa$variables$y_dr
aud<-rbind(
  audit(dr_core,"PRIMARY DR core",CORE),
  audit(amd_core,"PRIMARY AMD core",CORE),
  audit(dr_ins,"SUPP DR + insurance",paste(CORE,"+ insured_f")),
  audit(Aa,"ANALYSIS A (eye-care)",paste(CORE,"+ insured_f + recent_dilated_exam + factor(OPDURL4)")))
write.csv(aud,file.path(TBL,"t_model_audit_v7.csv"),row.names=FALSE); print(aud,row.names=FALSE)

# ============ 20. IPW WEIGHT DECOMPOSITION (gradable retinopathy respondents) ============
cat("\n#### 20. IPW WEIGHT DECOMPOSITION ####\n")
d$gradable_dr<-ifelse(is.na(d$OPDUARMA),0,1)
allsub<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
gbase<-svyglm(gradable_dr~agec+sex+race_bw, design=allsub, family=quasibinomial())
gext<-svyglm(gradable_dr~agec+sex+race_bw+dmflag+insured_f+educ_bw, design=allsub, family=quasibinomial())
predict_fill<-function(model,dat){need<-intersect(all.vars(formula(model))[-1],names(dat))
  comp<-stats::complete.cases(dat[,need,drop=FALSE]); p<-rep(NA,nrow(dat))
  if(sum(comp)>0)p[comp]<-as.vector(predict(model,newdata=dat[comp,,drop=FALSE],type="response")); p[is.na(p)]<-1; p}
grad_i<-which(!is.na(d$OPDUARMA))
decomp<-function(model,lab){
  p<-predict_fill(model,d); pf<-pmax(p,0.05)
  pg<-p[grad_i]; pfg<-pf[grad_i]; comb<-d$w_pooled[grad_i]/pfg; raw<-d$w_pooled[grad_i]
  data.frame(model=lab, n_gradable=length(grad_i),
    prob_min=round(min(pg),3), prob_median=round(median(pg),3), prob_max=round(max(pg),3),
    n_floored=sum(pg<0.05),
    invfactor_min=round(min(1/pfg),2), invfactor_median=round(median(1/pfg),2), invfactor_max=round(max(1/pfg),2),
    combwt_median=round(median(comb)), combwt_max=round(max(comb)),
    ess_kish=round(sum(comb)^2/sum(comb^2)), raw_ess=round(sum(raw)^2/sum(raw^2)),
    model_n=nrow(model$model))
}
ipwdec<-rbind(decomp(gbase,"base(age,sex,race)"), decomp(gext,"extended(+dm,insured,educ)"))
write.csv(ipwdec,file.path(TBL,"t_ipw_decomp_v7.csv"),row.names=FALSE); print(ipwdec,row.names=FALSE)

# ============ 21. AMD age gradient adjusted for severity + early-only age strata ============
cat("\n#### 21. AMD AGE vs SEVERITY ####\n")
amd_s<-SUB(paste(AMDcond,"& !is.na(amdstage)")); amd_s$variables$y<-amd_s$variables$y_amd
aud2<-audit(amd_s,"AMD age+severity",  "agec + sex + amdstage")
print(aud2,row.names=FALSE); write.csv(aud2,file.path(TBL,"t_amd_age_sev_v7.csv"),row.names=FALSE)
# early-AMD-only age strata gap (uses pre-computed ageband column)
eages<-list()
for(lv in c("40-59","60-69","70+")){
  s<-SUB(paste0("obj_amd_any==1 & OPDUARM==1 & !is.na(dx_amd) & as.character(ageband)=='",lv,"'"))
  w<-Wp(s,"y_amd"); eages[[length(eages)+1]]<-data.frame(stratum=paste0("Early AMD age ",lv),n=nrow(s$variables),est=w[1],lo=w[2],hi=w[3])
}
early_age<-do.call(rbind,eages); write.csv(early_age,file.path(TBL,"t_earlyamd_age_v7.csv"),row.names=FALSE); print(early_age,row.names=FALSE,digits=3)

# ============ 22. GA / neovascular overlap (mutual exclusivity at worse eye) ============
cat("\n#### 22. PHENOTYPE OVERLAP ####\n")
both<-sum(d$OPDUGA==1 & d$OPDUEXU==1, na.rm=TRUE); gao<-sum(d$OPDUGA==1,na.rm=TRUE); nvo<-sum(d$OPDUEXU==1,na.rm=TRUE)
ov<-data.frame(geographic_atrophy_n=gao, neovascular_n=nvo, both_worse_eye_n=both, late_amd_n=sum(d$OPDUARM==2,na.rm=TRUE))
write.csv(ov,file.path(TBL,"t_phenotype_overlap_v7.csv"),row.names=FALSE); print(ov,row.names=FALSE)
cat("\n== Done survey_analysis_v7 ==\n")
