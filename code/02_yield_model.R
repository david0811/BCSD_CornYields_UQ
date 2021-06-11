library(dplyr)
library(lfe)
library(fixest)
library(ggplot2)

# Load yield data (used for all models!)
usda <- read.csv('../data/usda/maize_county_yield_area.csv')
usda <- subset(usda, select=c('fips','year','lat','lon','log_yield', 'state'))
usda <- filter(usda, lon >= -100) # Select east of 100W meridian
usda <- filter(usda, year <= 2005) # Match GCM period
usda <- filter(usda, year >= 1956) # Match GCM period
usda <- merge(usda,  usda %>% count(fips)) # Filter to counties with >=50% coverage
usda <- filter(usda, n >= 25) # Filter to counties with >=50% coverage

##############################################
############### Fit all yield models for table
##############################################
# Climate data
gmfd.tavg <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tavg_hist.csv')
gmfd.tavg$tavg2 <- gmfd.tavg$tavg **2
gmfd.tmin <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tmin_hist.csv')
gmfd.tmin$tmin2 <- gmfd.tmin$tmin **2
gmfd.tmax <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tmax_hist.csv')
gmfd.tmax$tmax2 <- gmfd.tmax$tmax **2
gmfd.dd.p <- read.csv('../data/climate/GMFD/agvar_historical_gmfd.csv')
gmfd.dd.p$prcp2 <- gmfd.dd.p$prcp **2
gmfd <- merge(merge(merge(gmfd.dd.p, gmfd.tavg), gmfd.tmax), gmfd.tmin)

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2

# Models
fx.mod1 <- feols(log_yield ~ gdd + edd | state[year,year2] + fips, df)
fx.mod2 <- feols(log_yield ~ tavg + tavg2 | state[year,year2] + fips, df)
fx.mod3 <- feols(log_yield ~ tmin + tmin2 | state[year,year2] + fips, df)
fx.mod4 <- feols(log_yield ~ tmax + tmax2 | state[year,year2] + fips, df)
fx.mod5 <- feols(log_yield ~ gdd + edd + prcp + prcp2 | state[year,year2] + fips, df)
fx.mod6 <- feols(log_yield ~ tavg + tavg2 + prcp + prcp2 | state[year,year2] + fips, df)
fx.mod7 <- feols(log_yield ~ tmin + tmin2 + prcp + prcp2 | state[year,year2] + fips, df)
fx.mod8 <- feols(log_yield ~ tmax + tmax2 + prcp + prcp2 | state[year,year2] + fips, df)

# Table
etable(fx.mod1, fx.mod2, fx.mod3, fx.mod4, fx.mod5, fx.mod6, fx.mod7, fx.mod8, fitstat =~ . + aic + bic, tex=TRUE)

##############################################
############### Fit baseline yield model
##############################################
# Load climate data
gmfd <- read.csv('../data/climate/GMFD/agvar_historical_gmfd.csv')
gmfd$prcp2 <- gmfd$prcp**2

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2

# Fit model using felm
mod <- felm(log_yield ~ gdd + edd + prcp + prcp2 | factor(state) : poly(year,2) + factor(fips) | 0 | state, data<-df)
summary(mod)

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ gdd + edd + prcp + prcp2 | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)

# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/baseline_coeffs+95.csv")

# Save GMFD values
log_yield_predicted <- fitted.values(fx.mod)
df$log_yield_sim <- log_yield_predicted
write.csv(subset(df, select <- c(year, fips, state, gdd, edd, prcp, log_yield_sim)),
          "../data/yield/all_gmfd_historical.csv",
          row.names<-FALSE)

##############################################
############### Fit GDD + EDD yield model
##############################################
# Load climate data
gmfd <- read.csv('../data/climate/GMFD/agvar_historical_gmfd.csv')

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2

# Fit model using felm
mod <- felm(log_yield ~ gdd + edd | factor(state) : poly(year,2) + factor(fips) | 0 | state, data<-df)
summary(mod)

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ gdd + edd | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)

# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/degreedays_only_coeffs+95.csv")

##############################################
############### Fit Tavg quadratic yield model
##############################################
# Load climate data
gmfd <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tavg_hist.csv')

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2
df$tavg2 <- df$tavg**2

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ tavg + tavg2 | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)

# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/Tavg_only_coeffs+95.csv")

##############################################
############### Fit Tmin quadratic yield model
##############################################
# Load climate data
gmfd <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tmin_hist.csv')

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2
df$tmin2 <- df$tmin**2

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ tmin + tmin2 | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)

# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/Tmin_only_coeffs+95.csv")

##############################################
############### Fit Tmax quadratic yield model
##############################################
# Load climate data
gmfd <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tmax_hist.csv')

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2
df$tmax2 <- df$tmax**2

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ tmax + tmax2 | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)

# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/Tmax_only_coeffs+95.csv")

########################################################
############### Fit Tavg + precip quadratic yield model
########################################################
# Load climate data
gmfd.t <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tavg_hist.csv')
gmfd.p <- read.csv('../data/climate/GMFD/agvar_historical_gmfd.csv')
gmfd <- merge(gmfd.t, gmfd.p)
gmfd$prcp2 <- gmfd$prcp**2
gmfd$tavg2 <- gmfd$tavg**2

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ tavg + tavg2 + prcp + prcp2 | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)

# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/Tavg_prcp_coeffs+95.csv")

########################################################
############### Fit Tmin + precip quadratic yield model
########################################################
# Load climate data
gmfd.t <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tmin_hist.csv')
gmfd.p <- read.csv('../data/climate/GMFD/agvar_historical_gmfd.csv')
gmfd <- merge(gmfd.t, gmfd.p)
gmfd$prcp2 <- gmfd$prcp**2
gmfd$tmin2 <- gmfd$tmin**2

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ tmin + tmin2 + prcp + prcp2 | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)

# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/Tmin_prcp_coeffs+95.csv")

########################################################
############### Fit Tmax + precip quadratic yield model
########################################################
# Load climate data
gmfd.t <- read.csv('../data/climate/rawT_all/GMFD/gmfd_tmax_hist.csv')
gmfd.p <- read.csv('../data/climate/GMFD/agvar_historical_gmfd.csv')
gmfd <- merge(gmfd.t, gmfd.p)
gmfd$prcp2 <- gmfd$prcp**2
gmfd$tmax2 <- gmfd$tmax**2

# Merge
df <- merge(gmfd, usda)
df$year2 <- df$year**2

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ tmax + tmax2 + prcp + prcp2 | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)

# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/Tmax_prcp_coeffs+95.csv")


# ############################################################################
# ############### Apply yield regression to climate data (OLD!!)
# ############################################################################
# # NEX-GDDP
# nex.path <- '../data/climate/NEX-GDDP/hist'
# nex.models <- list.files(nex.path)
# for(name in nex.models) {
#   climod <- read.csv(paste(nex.path, name, sep<-"/"))
#   climod$prcp2 <- climod$prcp**2
#   climod$year2 <- climod$year**2
#   climod <- filter(climod, year >= 1956) # Match GCM period
#   climod$yield <- predict(fx.mod, climod)
#   
#   climod <- subset(climod, select <- -c(year2, prcp2))
#   
#   nex.out.path <- '../data/yield/NEX-GDDP/hist'
#   out.name <- paste("all", substr(name, 7, nchar(name)), sep<-"_")
#   write.csv(climod, paste(nex.out.path, out.name, sep<-"/"), row.names<-FALSE)
# }
# 
# # CMIP
# cmip.path <- '../data/climate/CMIP'
# cmip.models <- list.files(cmip.path)
# for(name in cmip.models) {
#   climod <- read.csv(paste(cmip.path, name, sep<-"/"))
#   climod$prcp2 <- climod$prcp**2
#   climod$year2 <- climod$year**2
#   climod <- filter(climod, year >= 1956) # Match GCM period
#   climod <- filter(climod, year <= 2005) # Match GCM period
#   climod$yield <- predict(fx.mod, climod)
#   
#   climod <- subset(climod, select <- -c(year2, prcp2) )
#   
#   cmip.out.path <- '../data/yield/CMIP/hist'
#   cmip.name <- substr(name, 1, nchar(name)-21)
#   cmip.name <- substr(cmip.name, 7, nchar(cmip.name))
#   out.name <- paste("all", cmip.name, sep<-"_")
#   out.name <- paste(out.name, "historical.csv", sep<-"_")
#   write.csv(climod, paste(cmip.out.path, out.name, sep<-"/"), row.names<-FALSE)
# }
