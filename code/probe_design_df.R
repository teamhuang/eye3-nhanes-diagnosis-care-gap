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
des<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~w_pooled,data=d,nest=TRUE)
DRcond<-"dm_dx==1 & obj_dr_any==1 & !is.na(dx_dr)"; AMDcond<-"obj_amd_any==1 & !is.na(dx_amd)"
SUB<-function(cond) subset(des, eval(parse(text=cond)))

psuinfo<-function(sg,lab){
  V<-sg$variables
  nstrata<-length(unique(V$SDMVSTRA))
  totPSU<-length(unique(paste(V$SDMVSTRA,V$SDMVPSU)))
  # PSUs per stratum distribution
  perstr<-tapply(V$SDMVPSU, V$SDMVSTRA, function(x) length(unique(x)))
  data.frame(subset=lab, n=nrow(V), strata=nstrata, total_PSU=totPSU,
             psu_per_stratum_min=min(perstr), psu_per_stratum_max=max(perstr),
             degf_survey=degf(sg), n_strata_with_1psu=sum(perstr==1))
}
full<-psuinfo(des,"Full pooled >=40 design")
dr<-psuinfo(SUB(DRcond),"DR responders")
amd<-psuinfo(SUB(AMDcond),"AMD responders")
drc<-psuinfo(SUB(paste(DRcond,"& !is.na(educ_bw) & !is.na(pir2)")),"DR core model")
amdc<-psuinfo(SUB(paste(AMDcond,"& !is.na(educ_bw) & !is.na(pir2)")),"AMD core model")
out<-rbind(full,dr,amd,drc,amdc); print(out,row.names=FALSE)
write.csv(out,file.path(TBL,"t_design_df_v6.csv"),row.names=FALSE)

# residual df actually used by svyglm summaries
cat("\n--- svyglm residual df (models) ---\n")
g1<-svyglm(y_dr~agec+sex+educ_bw+race_bw+pir2, design=SUB(paste(DRcond,"& !is.na(educ_bw) & !is.na(pir2)")), family=quasibinomial())
s1<-summary(g1); cat("DR core: residual degf=",s1$df,"\n")
sAdes<-SUB(paste(DRcond,"& !is.na(recent_dilated_exam) & !is.na(educ_bw) & !is.na(pir2)"))
gA<-svyglm(y_dr~recent_dilated_exam+agec+sex+educ_bw+race_bw+pir2+insured_f+factor(OPDURL4), design=sAdes, family=quasibinomial())
sA<-summary(gA); cat("Analysis-A: residual degf=",sA$df,"  n=",nrow(sAdes$variables),"\n")
cat("Analysis-A exam term: coef=",round(coef(sA)["recent_dilated_exam",1],4),
    " SE=",round(coef(sA)["recent_dilated_exam",2],4),
    " t=",round(coef(sA)["recent_dilated_exam",3],4),
    " Pr=",signif(coef(sA)["recent_dilated_exam",4],4),
    " aOR=",round(exp(coef(sA)["recent_dilated_exam",1]),3),
    " CI=",round(exp(coef(sA)["recent_dilated_exam",1]-qt(0.975,sA$df)*coef(sA)["recent_dilated_exam",2]),3),
    round(exp(coef(sA)["recent_dilated_exam",1]+qt(0.975,sA$df)*coef(sA)["recent_dilated_exam",2]),3),"\n")
