Sys.setenv(OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1)
suppressMessages({library(survey); library(mice)}); options(survey.lonely.psu="adjust"); set.seed(20261029)
CSV<-"C:/eye3/data/processed/analytic_dataset_v2.csv"; TBL<-"C:/eye3/results/tables"
d<-read.csv(CSV)
d$y_dr<-ifelse(is.na(d$dx_dr),NA,ifelse(d$dx_dr==1,0,1))
d$y_amd<-ifelse(is.na(d$dx_amd),NA,ifelse(d$dx_amd==1,0,1))
d$y_late<-d$y_amd
d$educ_bw<-factor(ifelse(d$educ==1,"<HS",ifelse(d$educ %in% c(2,3),"HS-or-more",NA)),levels=c("HS-or-more","<HS"))
d$race_bw<-factor(ifelse(d$RIDRETH1==3,"White","Non-White"),levels=c("White","Non-White"))
d$sex<-factor(ifelse(d$male==1,"Male","Female"),levels=c("Female","Male"))
d$insured_f<-factor(ifelse(d$insured==1,"Insured","Uninsured"),levels=c("Insured","Uninsured"))
d$agec<-ifelse(d$age>=85,85,d$age); d$pir2<-d$pir; d$cycle_n<-ifelse(d$cycle=="E",1,0)
d$modplus<-ifelse(d$OPDURL4>=3,1,ifelse(!is.na(d$OPDURL4),0,NA))
d$dmflag<-ifelse(d$dm_dx==1,1,0)
des<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
SUB<-function(cond) subset(des, eval(parse(text=cond)))
Wp<-function(s,var){r<-svyciprop(as.formula(paste0("~",var)),s,method="logit",na.rm=TRUE);ci<-confint(r);c(100*as.numeric(r),100*ci[1],100*ci[2])}
DRcond<-"dm_dx==1 & obj_dr_any==1 & !is.na(dx_dr)"; AMDcond<-"obj_amd_any==1 & !is.na(dx_amd)"

cat("#### 16. MODERATE-OR-WORSE DR combined diagnosis gap (reviewer item 6) ####\n")
mw<-SUB(paste(DRcond,"& OPDURL4>=3"))   # moderate+severe/proliferative, diabetes, retinopathy, responders
w<-Wp(mw,"y_dr")
modworse<-data.frame(stratum="Moderate-or-worse retinopathy (DR, responders)", n=nrow(mw$variables),
                     est=w[1], lo=w[2], hi=w[3])
print(modworse,row.names=FALSE,digits=3); write.csv(modworse,file.path(TBL,"t_modworse_gap_v6.csv"),row.names=FALSE)

cat("\n#### 17. IPW gradability: extended model + weight diagnostics + discordance selection sensitivity ####\n")
d$gradable_dr<-ifelse(is.na(d$OPDUARMA),0,1)
allsub<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
gbase<-svyglm(gradable_dr~agec+sex+race_bw, design=allsub, family=quasibinomial())
gext<-svyglm(gradable_dr~agec+sex+race_bw+dmflag+insured_f+educ_bw, design=allsub, family=quasibinomial())
# safe predictor: predict on rows with complete covariates, fill 1 (=no reweighting) for the rest
predict_fill<-function(model, dat, rhsvars){
  need<-intersect(all.vars(formula(model))[-1], names(dat))
  comp<-stats::complete.cases(dat[,need,drop=FALSE])
  p<-rep(NA, nrow(dat))
  if(sum(comp)>0) p[comp]<-as.vector(predict(model, newdata=dat[comp,,drop=FALSE], type="response"))
  p[is.na(p)]<-1
  pmax(p, 0.05)
}
pbase<-predict_fill(gbase, d, NULL); pext<-predict_fill(gext, d, NULL)
grad_i<-which(!is.na(d$OPDUARMA))   # gradable retinopathy respondents for prevalence denominators
wsum<-function(p,lab){
  wt<-d$w_pooled[grad_i]/p[grad_i]
  data.frame(model=lab, n_gradable=length(grad_i), wt_min=quantile(wt,0)[1], wt_median=median(wt),
             wt_max=quantile(wt,1)[1], ipw_ess=(sum(wt))^2/sum(wt^2),
             raw_ess=(sum(d$w_pooled[grad_i])^2)/sum(d$w_pooled[grad_i]^2), floor_p=0.05)
}
wd<-rbind(wsum(pbase,"base(age,sex,race)"), wsum(pext,"extended(+dm,insured,educ)"))
write.csv(wd,file.path(TBL,"t_ipw_weightdiag_v6.csv"),row.names=FALSE); print(wd,row.names=FALSE,digits=4)
# extended-model IPW whole-population prevalence
d$w_ipw_ext<-d$w_pooled/pext
dipw_ext<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_ipw_ext,data=d,nest=TRUE)
prev_ext<-data.frame(measure=c("Any retinopathy (all >=40)","Any AMD (all >=40)"),
  naive=c(as.numeric(svymean(~obj_dr_any, subset(allsub, !is.na(OPDUARMA)),na.rm=TRUE)),
          as.numeric(svymean(~obj_amd_any, subset(allsub, !is.na(OPDUARM)),na.rm=TRUE)))*100,
  ipw_ext=c(as.numeric(svymean(~obj_dr_any, dipw_ext,na.rm=TRUE)),
            as.numeric(svymean(~obj_amd_any, dipw_ext,na.rm=TRUE)))*100)
write.csv(prev_ext,file.path(TBL,"t_ipw_prevalence_ext_v6.csv"),row.names=FALSE); print(prev_ext,row.names=FALSE,digits=3)
# DISCORDANCE selection sensitivity: reweight responders by 1/P(gradable|X)
ipw_des<-function(cond, pvec){
  sd<-SUB(cond); V<-sd$variables
  p<-predict_fill(gext, V, NULL)
  V$wi<-V$w_pooled/p
  svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~wi,data=V,nest=TRUE)
}
g_dr_unw<-Wp(SUB(DRcond),"y_dr"); g_amd_unw<-Wp(SUB(AMDcond),"y_amd")
g_dr_ipw<-Wp(ipw_des(DRcond, pext),"y_dr"); g_amd_ipw<-Wp(ipw_des(AMDcond, pext),"y_amd")
disc_sel<-data.frame(outcome=c("DR diagnosis gap","AMD diagnosis gap"),
  responders_weighted=c(sprintf("%.1f (%.1f-%.1f)",g_dr_unw[1],g_dr_unw[2],g_dr_unw[3]),sprintf("%.1f (%.1f-%.1f)",g_amd_unw[1],g_amd_unw[2],g_amd_unw[3])),
  ipw_gradability=c(sprintf("%.1f (%.1f-%.1f)",g_dr_ipw[1],g_dr_ipw[2],g_dr_ipw[3]),sprintf("%.1f (%.1f-%.1f)",g_amd_ipw[1],g_amd_ipw[2],g_amd_ipw[3])))
write.csv(disc_sel,file.path(TBL,"t_discordance_selection_v6.csv"),row.names=FALSE); print(disc_sel,row.names=FALSE)

cat("\n#### 18. MI diagnostics + missingness mechanism (reviewer item 4) ####\n")
drfull<-d[which(d$dm_dx==1 & d$obj_dr_any==1 & !is.na(d$dx_dr)),]
X<-data.frame(y_dr=drfull$y_dr, agec=drfull$agec, sex=as.integer(drfull$sex=="Male"),
              race=as.integer(drfull$race_bw=="Non-White"), insured=as.integer(drfull$insured==1),
              sev=drfull$OPDURL4, cycle=drfull$cycle_n, pir=drfull$pir2,
              educ=factor(ifelse(drfull$educ_bw=="<HS","<HS","HS-or-more"),levels=c("HS-or-more","<HS")))
missdiag<-data.frame(variable=c("y_dr","agec","sex","race","insured","sev","cycle","pir","educ"),
                     pct_missing=round(100*colMeans(is.na(X)),1))
set.seed(20261029)
ini<-mice(X, m=20, maxit=10, method=c("","","","","","","","pmm","logreg"), printFlag=FALSE, seed=20261029)
TERMS<-c("agec","sexMale","educ_bw<HS","race_bwNon-White","pir2")
coefs<-t(sapply(1:20, function(mi){
  cc<-mice::complete(ini,mi)
  cc$educ_bw<-cc$educ
  cc$sex<-factor(ifelse(cc$sex==1,"Male","Female"),levels=c("Female","Male"))
  cc$race_bw<-factor(ifelse(cc$race==1,"Non-White","White"),levels=c("White","Non-White"))
  cc$pir2<-cc$pir; cc$SDMVPSU<-drfull$SDMVPSU; cc$SDMVSTRA<-drfull$SDMVSTRA; cc$w_pooled<-drfull$w_pooled
  dsn<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=cc,nest=TRUE)
  cf<-coef(summary(svyglm(y_dr~agec+sex+educ_bw+race_bw+pir2,design=dsn,family=quasibinomial())))
  cf[TERMS,1]
}))
colnames(coefs)<-TERMS
pirdiag<-data.frame(term=TERMS, mean_logOR=colMeans(coefs), aOR=exp(colMeans(coefs)),
                    min_aOR=exp(apply(coefs,2,min)), max_aOR=exp(apply(coefs,2,max)),
                    sd_across_m=apply(coefs,2,sd), n_imputations=20)
write.csv(missdiag,file.path(TBL,"t_mi_missingness_v6.csv"),row.names=FALSE); print(missdiag,row.names=FALSE)
write.csv(pirdiag,file.path(TBL,"t_mi_perimputation_v6.csv"),row.names=FALSE); print(pirdiag,row.names=FALSE,digits=3)
# missingness-mechanism descriptive models (educ & pir missing among DR responders)
drfull$educ_missing<-as.integer(!(drfull$educ %in% c(1,2,3)))
drfull$pir_missing<-as.integer(is.na(drfull$pir2))
drfull$sev_plus<-ifelse(drfull$OPDURL4>=3,1,0)
mdes<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=drfull,nest=TRUE)
me<-svyglm(educ_missing~agec+sex+race_bw+dm_dx+insured_f+y_dr+cycle_n, design=mdes, family=quasibinomial())
mp<-svyglm(pir_missing~agec+sex+race_bw+dm_dx+insured_f+y_dr+cycle_n, design=mdes, family=quasibinomial())
sig_tab<-function(g,lab){sm<-coef(summary(g)); sm<-sm[rownames(sm)!="(Intercept)",,drop=FALSE]
  data.frame(model=lab, term=rownames(sm), OR=exp(sm[,1]), p=sm[,4])}
mm<-rbind(sig_tab(me,"Education missing"),sig_tab(mp,"Income missing"))
write.csv(mm,file.path(TBL,"t_missing_mechanism_v6.csv"),row.names=FALSE); print(mm,row.names=FALSE,digits=3)
cat("\n== Done survey_analysis_v6 ==\n")
