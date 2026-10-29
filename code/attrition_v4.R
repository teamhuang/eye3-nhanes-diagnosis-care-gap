d<-read.csv("C:/eye3/data/processed/analytic_dataset_v2.csv")
eb<-ifelse(d$educ==1,"<HS",ifelse(d$educ %in% c(2,3),"HS+","NA"))
idx<-which(d$dm_dx==1 & d$obj_dr_any==1 & !is.na(d$dx_dr))
dr<-d[idx,]; dr$y<-ifelse(dr$dx_dr==1,0,1); dr$eb<-eb[idx]
complete<- dr$eb!="NA" & !is.na(dr$pir)
ent<-dr[complete,]; exc<-dr[!complete,]
cat("entrants",nrow(ent),"excluded",nrow(exc),"\n")
f<-function(x) c(age=mean(x$age,na.rm=TRUE),male=100*mean(x$male,na.rm=TRUE),
                 insured=100*mean(x$insured,na.rm=TRUE),exam=100*mean(x$recent_dilated_exam,na.rm=TRUE),
                 nody=100*mean(x$y,na.rm=TRUE))
print(round(rbind(entrants=f(ent),excluded=f(exc)),1))
cat("age_p=",round(t.test(ent$age,exc$age)$p.value,3),
    "nody_p=",round(t.test(ent$y,exc$y)$p.value,3),"\n")
write.csv(round(rbind(entrants=f(ent),excluded=f(exc)),1),"C:/eye3/results/tables/t_attrition_v4.csv")
