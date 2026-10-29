Sys.setenv(OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1)
suppressMessages({library(survey); library(mitools)}); options(survey.lonely.psu="adjust"); set.seed(20261029)
CSV<-"C:/eye3/data/processed/analytic_dataset_v2.csv"; TBL<-"C:/eye3/results/tables"
d<-read.csv(CSV)
d$y_dr<-ifelse(is.na(d$dx_dr),NA,ifelse(d$dx_dr==1,0,1))
d$y_amd<-ifelse(is.na(d$dx_amd),NA,ifelse(d$dx_amd==1,0,1))
d$y_late<-ifelse(is.na(d$dx_amd),NA,ifelse(d$dx_amd==1,0,1))
d$educ_bw<-factor(ifelse(d$educ==1,"<HS",ifelse(d$educ %in% c(2,3),"HS-or-more",NA)),levels=c("HS-or-more","<HS"))
d$race_bw<-factor(ifelse(d$RIDRETH1==3,"White","Non-White"),levels=c("White","Non-White"))
d$sex<-factor(ifelse(d$male==1,"Male","Female"),levels=c("Female","Male"))
d$insured_f<-factor(ifelse(d$insured==1,"Insured","Uninsured"),levels=c("Insured","Uninsured"))
d$agec<-ifelse(d$age>=85,85,d$age); d$pir2<-d$pir
d$cycle_n<-ifelse(d$cycle=="E",1,0)
des<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
SUB<-function(cond) subset(des, eval(parse(text=cond)))
Wp<-function(s,var){r<-svyciprop(as.formula(paste0("~",var)),s,method="logit",na.rm=TRUE);ci<-confint(r);c(100*as.numeric(r),100*ci[1],100*ci[2])}
DRcond<-"dm_dx==1 & obj_dr_any==1 & !is.na(dx_dr)"; AMDcond<-"obj_amd_any==1 & !is.na(dx_amd)"

cat("#### 9. AMD SEVERITY TIERS (early / late / GA / NV) ####\n")
rows<-list()
for(spec in list(c("Early AMD","obj_amd_any==1 & OPDUARM==1 & !is.na(dx_amd)"),
                 c("Late AMD","obj_amd_late==1 & !is.na(dx_amd)"),
                 c("Geographic atrophy","obj_amd_late==1 & OPDUGA==1 & !is.na(dx_amd)"),
                 c("Neovascular/exudative","obj_amd_late==1 & OPDUEXU==1 & !is.na(dx_amd)"))){
  s<-SUB(spec[2]); w<-Wp(s,"y_late"); rows[[length(rows)+1]]<-data.frame(tier=spec[1],n=nrow(s$variables),est=w[1],lo=w[2],hi=w[3])
}
amdsev<-do.call(rbind,rows); write.csv(amdsev,file.path(TBL,"t_amd_severity_v5.csv"),row.names=FALSE); print(amdsev,row.names=FALSE,digits=3)
# assertion GA+NV == late
stopifnot(amdsev$n[1+1]==55, amdsev$n[3]+amdsev$n[4]==55)

cat("\n#### 10. NON-RESPONSE EXTREME-SCENARIO BOUNDS (weighted) ####\n")
# DR: base = dm & retinopathy (319); responders have y_dr; non-responders (dx_dr NA) forced 0 (diagnosed) or 1 (undiagnosed)
base_dr<-d[which(d$dm_dx==1 & d$obj_dr_any==1),]
bdes<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=base_dr,nest=TRUE)
lo_y<-ifelse(is.na(base_dr$dx_dr),0, base_dr$y_dr); hi_y<-ifelse(is.na(base_dr$dx_dr),1, base_dr$y_dr)
bdes$variables$y_lo<-lo_y; bdes$variables$y_hi<-hi_y
gap_lo<-Wp(bdes,"y_lo"); gap_hi<-Wp(bdes,"y_hi")
base_amd<-d[which(d$obj_amd_any==1),]; ades<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=base_amd,nest=TRUE)
ades$variables$y_lo<-ifelse(is.na(base_amd$dx_amd),0, base_amd$y_amd); ades$variables$y_hi<-ifelse(is.na(base_amd$dx_amd),1, base_amd$y_amd)
agap_lo<-Wp(ades,"y_lo"); agap_hi<-Wp(ades,"y_hi")
nr<-data.frame(cohort=c("DR (n=319 base; 6 non-responders)","AMD (n=441 base; 5 non-responders)"),
  responders_only=c(sprintf("%.1f (%.1f-%.1f)",Wp(SUB(DRcond),"y_dr")[1],Wp(SUB(DRcond),"y_dr")[2],Wp(SUB(DRcond),"y_dr")[3]),
                    sprintf("%.1f (%.1f-%.1f)",Wp(SUB(AMDcond),"y_amd")[1],Wp(SUB(AMDcond),"y_amd")[2],Wp(SUB(AMDcond),"y_amd")[3])),
  all_nonresponder_diagnosed=c(sprintf("%.1f (%.1f-%.1f)",gap_lo[1],gap_lo[2],gap_lo[3]),sprintf("%.1f (%.1f-%.1f)",agap_lo[1],agap_lo[2],agap_lo[3])),
  all_nonresponder_undiagnosed=c(sprintf("%.1f (%.1f-%.1f)",gap_hi[1],gap_hi[2],gap_hi[3]),sprintf("%.1f (%.1f-%.1f)",agap_hi[1],agap_hi[2],agap_hi[3])))
write.csv(nr,file.path(TBL,"t_nonresponse_bounds_v5.csv"),row.names=FALSE); print(nr,row.names=FALSE)

cat("\n#### 11. REDUCED MODELS (drop high-missing covariates) ####\n")
fitq<-function(s,rhs,desc){g<-svyglm(as.formula(paste0("y_dr ~ ",rhs)),design=s,family=quasibinomial());sm<-summary(g)
  tc<-qt(0.975, max(1,degf(s)-g$rank+1))
  cf<-rownames(sm$coefficients);cf<-cf[cf!="(Intercept)"]
  data.frame(model=desc,term=cf,aOR=exp(sm$coefficients[cf,1]),lo=exp(sm$coefficients[cf,1]-tc*sm$coefficients[cf,2]),
             hi=exp(sm$coefficients[cf,1]+tc*sm$coefficients[cf,2]),p=sm$coefficients[cf,4],n=nrow(s$variables))}
sR1<-SUB(paste(DRcond,"& !is.na(educ_bw) & !is.na(pir2)"))                    # full (reference)
sR2<-SUB(paste(DRcond,"& !is.na(pir2)"))                                       # drop education
sR3<-SUB(paste(DRcond))                                                        # drop education+income (all 313)
red<-rbind(fitq(sR1,"agec + sex + educ_bw + race_bw + pir2","Full core (educ+income, n=187)"),
           fitq(sR2,"agec + sex + race_bw + pir2","Drop education (income kept)"),
           fitq(sR3,"agec + sex + race_bw","Drop education+income (all responders)"))
write.csv(red,file.path(TBL,"t_reduced_models_v5.csv"),row.names=FALSE); print(red,row.names=FALSE,digits=3)

cat("\n#### 12. MULTIPLE IMPUTATION (mice, m=20) + Rubin pooling (manual) ####\n")
mi_res<-tryCatch({
  suppressMessages(library(mice))
  dr<-d[which(d$dm_dx==1 & d$obj_dr_any==1 & !is.na(d$dx_dr)),]
  X<-data.frame(y_dr=dr$y_dr, agec=dr$agec, sex=as.integer(dr$sex=="Male"),
                race=as.integer(dr$race_bw=="Non-White"), insured=as.integer(dr$insured==1),
                sev=dr$OPDURL4, cycle=dr$cycle_n, pir=dr$pir2,
                educ=factor(ifelse(dr$educ_bw=="<HS","<HS","HS-or-more"),levels=c("HS-or-more","<HS")))
  set.seed(20261029)
  ini<-mice(X, m=20, method=c("","","","","","","","pmm","logreg"), printFlag=FALSE, seed=20261029)
  TERMS<-c("agec","sexMale","educ_bw<HS","race_bwNon-White","pir2")
  fits<-lapply(1:20, function(m){
    cc<-mice::complete(ini,m)
    cc$educ_bw<-cc$educ
    cc$sex<-factor(ifelse(cc$sex==1,"Male","Female"),levels=c("Female","Male"))
    cc$race_bw<-factor(ifelse(cc$race==1,"Non-White","White"),levels=c("White","Non-White"))
    cc$pir2<-cc$pir
    cc$SDMVPSU<-dr$SDMVPSU; cc$SDMVSTRA<-dr$SDMVSTRA; cc$w_pooled<-dr$w_pooled
    dsn<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=cc,nest=TRUE)
    svyglm(y_dr~agec+sex+educ_bw+race_bw+pir2,design=dsn,family=quasibinomial())
  })
  coefs<-t(sapply(fits,function(g){cf<-coef(summary(g)); cf[TERMS,1]}))
  ses  <-t(sapply(fits,function(g){cf<-coef(summary(g)); cf[TERMS,2]}))
  mN<-20
  Qbar<-colMeans(coefs); Ubar<-colMeans(ses^2); B<-apply(coefs,2,var); Tt<-Ubar+(1+1/mN)*B
  dfb<-ifelse(Tt>0,(mN-1)*(1+Ubar/Tt)^2, Inf)
  stat<-Qbar/sqrt(Tt); pv<-2*pt(-abs(stat), df=dfb)
  tcrit<-qt(0.975, df=dfb)
  data.frame(model="MI (m=20, Rubin-pooled)", term=TERMS, aOR=exp(Qbar),
             lo=exp(Qbar-tcrit*sqrt(Tt)), hi=exp(Qbar+tcrit*sqrt(Tt)), p=pv, n=313)
}, error=function(e){cat("MI failed:",conditionMessage(e),"-- reporting NA\n");data.frame(model="MI failed",term=NA,aOR=NA,lo=NA,hi=NA,p=NA,n=NA)})
write.csv(mi_res,file.path(TBL,"t_mi_v5.csv"),row.names=FALSE); print(mi_res,row.names=FALSE,digits=3)

cat("\n#### 13. GRADABILITY: comparison + IPW prevalence ####\n")
d$gradable_dr<-ifelse(is.na(d$OPDUARMA),0,1)
comp<-function(g){s<-d[which(d$gradable_dr==g & !is.na(d$age)),];c(n=nrow(s),age=mean(s$age,na.rm=TRUE),male=100*mean(s$male,na.rm=TRUE),
  dm=100*mean(s$dm_dx==1,na.rm=TRUE),nonwhite=100*mean(s$RIDRETH1!=3,na.rm=TRUE),insured=100*mean(s$insured==1,na.rm=TRUE),
  educ_lt_hs=100*mean(s$educ==1,na.rm=TRUE))}
gr<-rbind(gradable=comp(1),ungradable=comp(0)); write.csv(gr,file.path(TBL,"t_gradability_v5.csv")); print(round(gr,1))
# IPW for gradability using always-complete covariates (age, sex, race); recompute AMD/DR prevalence
allsub<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
gmod<-svyglm(gradable_dr~agec+sex+race_bw, design=allsub, family=quasibinomial())
d$pred_g<-pmax(as.vector(predict(gmod,newdata=d,type="response")),0.05)
d$w_ipooled<-d$w_pooled/d$pred_g
dipw<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_ipooled,data=d,nest=TRUE)
naive_dr<-as.numeric(svymean(~obj_dr_any, subset(allsub, !is.na(OPDUARMA)),na.rm=TRUE))
naive_amd<-as.numeric(svymean(~obj_amd_any, subset(allsub, !is.na(OPDUARM)),na.rm=TRUE))
ipw_dr<-as.numeric(svymean(~obj_dr_any, dipw,na.rm=TRUE))
ipw_amd<-as.numeric(svymean(~obj_amd_any, dipw,na.rm=TRUE))
ipw<-data.frame(measure=c("Any retinopathy (all >=40)","Any AMD (all >=40)"),
                naive_pct=c(100*naive_dr,100*naive_amd), ipw_gradability_pct=c(100*ipw_dr,100*ipw_amd))
write.csv(ipw,file.path(TBL,"t_ipw_prevalence_v5.csv"),row.names=FALSE); print(ipw,row.names=FALSE,digits=3)

cat("\n#### 14. DESIGN df per analytic subset ####\n")
dd<-function(cond,lab){s<-SUB(cond);nps<-length(unique(s$variables$SDMVPSU));nst<-length(unique(s$variables$SDMVSTRA));
  data.frame(subset=lab,n=nrow(s$variables),strata=nst,psu=nps,df_taylor=nst-nps)}
dfn<-rbind(dd(DRcond,"DR responders (313)"),dd(AMDcond,"AMD responders (436)"),
  dd(paste(DRcond,"& !is.na(educ_bw) & !is.na(pir2)"),"DR core model (187)"),
  dd(paste(AMDcond,"& !is.na(educ_bw) & !is.na(pir2)"),"AMD core model (226)"))
write.csv(dfn,file.path(TBL,"t_design_df_v5.csv"),row.names=FALSE); print(dfn,row.names=FALSE)

cat("\n#### 15. NHIS standardisation: design-covariance reweighting (age + age-sex) ####\n")
nhis<-read.csv("C:/eye3/data/processed/nhis_adult_2016_eye40plus.csv")
nhis$md<-as.numeric(ifelse(nhis$eye_mac %in% c(0,1),nhis$eye_mac,NA))
bands<-function(a) cut(a,breaks=c(40,50,60,70,80,200),labels=c("40-49","50-59","60-69","70-79","80+"),right=FALSE,include.lowest=TRUE)
BLEV<-levels(bands(45))
nhis$band<-factor(bands(nhis$age40plus_num),levels=BLEV)
ndes<-svydesign(ids=~psu,strata=~strata,weights=~wt,data=nhis,nest=TRUE)
# Standard-population weights from NHANES (FIXED): age-band proportions
d$band<-factor(bands(d$age),levels=BLEV)
for(lv in BLEV) d[[paste0("bd_",make.names(lv))]]<-as.integer(d$band==lv)
bdcols<-paste0("bd_",make.names(BLEV)); desB<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
bp<-as.vector(svymean(as.formula(paste("~",paste(bdcols,collapse="+"))),desB)); names(bp)<-BLEV; std_w<-bp/sum(bp)
# Reweighting identity: w_std_i = wt_i * stdw(group_i)/Wh(group_i), Wh = sum of wt over RESPONDERS in group
# => svymean(~md, w_std, na.rm=TRUE) equals sum_b stdw_b*rate_b AND carries full design covariance.
std_by_group<-function(group_levels, nhis_group, nhis_wt, resp, std_pop){
  Wh<-tapply(nhis_wt[resp], factor(nhis_group[resp], levels=group_levels), sum)   # responder weighted N per group
  spc<-as.numeric(std_pop)[match(group_levels, names(std_pop))]
  denom<-ifelse(is.na(Wh)|Wh<=0, NA, Wh)
  scale<-spc/denom
  wstd<-nhis_wt * scale[match(nhis_group, group_levels)]
  wstd[!is.finite(wstd)]<-0
  data.frame(wstd=wstd, scale=scale[match(nhis_group, group_levels)], Wh=denom[match(nhis_group, group_levels)])
}
resp<-!is.na(nhis$md)
age_rw<-std_by_group(BLEV, as.character(nhis$band), nhis$wt, resp, std_w)
nhis$w_std_age<-age_rw$wstd
des_age<-svydesign(ids=~psu,strata=~strata,weights=~w_std_age,data=nhis,nest=TRUE)
std_age<-svymean(~md, des_age, na.rm=TRUE); ci_age<-confint(std_age)
# Age-and-sex standardisation (10 cells); standard population = NHANES joint cell proportions
nhis$sexb<-factor(ifelse(nhis$SEX==1,"M","F"),levels=c("M","F")); d$sexb<-factor(ifelse(d$male==1,"M","F"),levels=c("M","F"))
cellname<-function(b,s) paste(b,s)
d$cell<-factor(paste(d$band, d$sexb))
CLEV<-as.vector(t(outer(BLEV,c("M","F"),cellname)))
d$cellf<-factor(paste(d$band, d$sexb), levels=CLEV); nhis$cellf<-factor(paste(nhis$band, nhis$sexb), levels=CLEV)
for(cv in CLEV) d[[paste0("cl_",make.names(cv))]]<-as.integer(d$cellf==cv)
clcols<-paste0("cl_",make.names(CLEV))
desC<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
cp<-as.vector(svymean(as.formula(paste("~",paste(clcols,collapse="+"))),desC)); names(cp)<-CLEV; std_w2<-cp/sum(cp)
agesex_rw<-std_by_group(CLEV, as.character(nhis$cellf), nhis$wt, resp, std_w2)
nhis$w_std_age_sex<-agesex_rw$wstd
des_agesex<-svydesign(ids=~psu,strata=~strata,weights=~w_std_age_sex,data=nhis,nest=TRUE)
std_agesex<-svymean(~md, des_agesex, na.rm=TRUE); ci_agesex<-confint(std_agesex)
# crude weighted
mmd<-svymean(~md,ndes,na.rm=TRUE); cc<-confint(mmd); cw<-as.numeric(mmd)
out<-data.frame(quantity=c("NHIS crude weighted (>=40)",
                           "NHIS age-standardised (design covariance; std weights fixed from NHANES)",
                           "NHIS age-and-sex-standardised (design covariance; std weights fixed from NHANES)"),
  est_pct=c(100*cw,100*as.numeric(std_age),100*as.numeric(std_agesex)),
  lo_pct=c(100*as.numeric(cc[1]),100*as.numeric(ci_age[1]),100*as.numeric(ci_agesex[1])),
  hi_pct=c(100*as.numeric(cc[2]),100*as.numeric(ci_age[2]),100*as.numeric(ci_agesex[2])))
write.csv(out,file.path(TBL,"t_nhis_std_versions_v5.csv"),row.names=FALSE); print(out,row.names=FALSE,digits=3)
# per-band rate + std-weight table
by_band<-as.data.frame(svyby(~md,~band,ndes,svymean,na.rm=TRUE)); by_band$band<-as.character(by_band$band)
rate_pct<-100*as.numeric(by_band$md[match(BLEV,by_band$band)])
Wh_band<-tapply(nhis$wt[resp], factor(nhis$band[resp], levels=BLEV), sum)
write.csv(data.frame(band=BLEV, rate_pct=rate_pct, responder_weighted_N=as.numeric(Wh_band), std_weight=as.numeric(std_w)),file.path(TBL,"t_nhis_std_cov_v5.csv"),row.names=FALSE)
cat("\n== Done survey_analysis_v5 ==\n")
