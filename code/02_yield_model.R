library(dplyr)
library(lfe)
library(fixest)
library(ggplot2)

######################################
############### Fit yield model
######################################
# Load climate data
gmfd <- read.csv('../data/climate/GMFD/agvar_historical_gmfd.csv')
gmfd$prcp2 <- gmfd$prcp**2

# Load yield data
usda <- read.csv('../data/usda/maize_county_yield_area.csv')
usda <- subset(usda, select=c('fips','year','lat','lon','log_yield', 'state'))
usda <- filter(usda, lon >= -100) # Select east of 100W meridian

# Merge
df = merge(gmfd, usda)
df <- filter(df, year <= 2005) # Match GCM period
df$year2 <- df$year**2

# Fit model using felm
mod <- felm(log_yield ~ gdd + edd + prcp + prcp2 | factor(state) : poly(year,2) + factor(fips) | 0 | state, data=df)
summary(mod)

# Fit model using fixest (easier for getting predictions)
fx.mod <- feols(log_yield ~ gdd + edd + prcp + prcp2 | state[year,year2] + fips, df)
summary(fx.mod, cluster=~state)
# Results
coefplot(fx.mod)
res <- data.frame(coef(fx.mod), confint(fx.mod, cluster=~state))
colnames(res) <- c('coeff','2.5','97.5')
write.csv(res, "../data/yield/regression_coeffs+95.csv")
fe.res <- data.frame(fixef(fx.mod)$fips)
colnames(fe.res) <- c('fe')
write.csv(fe.res, "../data/yield/regression_fips_fe.csv")

plot(fixef(fx.mod))

# Save GMFD values
log_yield_predicted <- fitted.values(fx.mod)
df$log_yield_sim <- log_yield_predicted
write.csv(subset(df, select = c(year, fips, state, gdd, edd, prcp, log_yield_sim)),
          "../data/yield/GMFD/all_gmfd_historical.csv",
          row.names=FALSE)

nex.path <- '../data/climate/NEX-GDDP/hist'
nex.models <- list.files(nex.path)
climod <- read.csv(paste(nex.path, nex.models[2], sep="/"))
climod$prcp2 <- climod$prcp**2
climod$year2 <- climod$year**2
climod <- filter(climod, year >= 1956) # Match GCM period
climod$yield <- predict(fx.mod, climod)


############################################################################
############### Apply yield regression to climate data
############################################################################
# NEX-GDDP
nex.path <- '../data/climate/NEX-GDDP/hist'
nex.models <- list.files(nex.path)
for(name in nex.models) {
  climod <- read.csv(paste(nex.path, name, sep="/"))
  climod$prcp2 <- climod$prcp**2
  climod$year2 <- climod$year**2
  climod <- filter(climod, year >= 1956) # Match GCM period
  climod$yield <- predict(fx.mod, climod)
  
  climod <- subset(climod, select = -c(year2, prcp2))
  
  nex.out.path <- '../data/yield/NEX-GDDP/hist'
  out.name <- paste("all", substr(name, 7, nchar(name)), sep="_")
  write.csv(climod, paste(nex.out.path, out.name, sep="/"), row.names=FALSE)
}

# CMIP
cmip.path <- '../data/climate/CMIP'
cmip.models <- list.files(cmip.path)
for(name in cmip.models) {
  climod <- read.csv(paste(cmip.path, name, sep="/"))
  climod$prcp2 <- climod$prcp**2
  climod$year2 <- climod$year**2
  climod <- filter(climod, year >= 1956) # Match GCM period
  climod <- filter(climod, year <= 2005) # Match GCM period
  climod$yield <- predict(fx.mod, climod)
  
  climod <- subset(climod, select = -c(year2, prcp2) )
  
  cmip.out.path <- '../data/yield/CMIP/hist'
  cmip.name <- substr(name, 1, nchar(name)-21)
  cmip.name <- substr(cmip.name, 7, nchar(cmip.name))
  out.name <- paste("all", cmip.name, sep="_")
  out.name <- paste(out.name, "historical.csv", sep="_")
  write.csv(climod, paste(cmip.out.path, out.name, sep="/"), row.names=FALSE)
}
