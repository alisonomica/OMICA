
# ---- Generate sample random data ----
library(dplyr)
library(tibble)
library(purrr)

# define function
generateRandomK <- function(k, nsamples) {
  randomprobs <- function(k) {
    probsout <- diff(c(0, sort(runif(k - 1)), 1))
    enframe(probsout)
  }
  probsdf <- map_df(1:nsamples, ~randomprobs(k))
  probsdf <- mutate(probsdf, sampleID = rep(1:nsamples, each = k))
  probsdf <- select(probsdf, sampleID, popGroup = name, prob = value)
  return(probsdf)
}

#locations <- c("East", "West", "North", "South", "Unknown")
#locdata <- tibble(
#  sampleID = 1:131,
#  loc = sample(locations, 131, replace = TRUE)
#)

# Generate data for k=2
kdf2 <- generateRandomK(k = 2, nsamples = 131)
#kdf2 <- left_join(kdf2, locdata)
newkdf2 <- reshape(as.data.frame(kdf2), direction="wide", idvar = "sampleID", timevar = "popGroup", v.names = 'prob')

# k=3
kdf3 <- generateRandomK(k = 3, nsamples = 131)
#kdf3 <- left_join(kdf3, locdata)
newkdf3 <- reshape(as.data.frame(kdf3), direction="wide", idvar = "sampleID", timevar = "popGroup", v.names = 'prob')

# k=4
kdf4 <- generateRandomK(k = 4, nsamples = 131)
#kdf4 <- left_join(kdf4, locdata)
newkdf4 <- reshape(as.data.frame(kdf4), direction="wide", idvar = "sampleID", timevar = "popGroup", v.names = 'prob')

# ---- Admixture bar plot ----
library(ggplot2)
library(forcats)

plot_ancestry <- function(probfile, width = 18, height = 18, popsort){
  # Load file 
  df <- read.delim(probfile)
  
  # Sort individuals according to popsort
  levels <- order(df[,popsort+1], decreasing = TRUE)

  # Melt data.frame from wide to long format
  df <- reshape(df, direction = "long", idvar = colnames(df)[1], varying = list(2:ncol(df)), timevar = "popGroup",
                v.names = "prob")
  
  # Plot
  groups <- length(levels(factor(df[,2])))
  title <- paste(groups, "Groups")
  
  kplot <-
    ggplot(df, aes(factor(df[,1], levels = levels), prob, fill = factor(popGroup))) +
    geom_col(color = "gray", size = 0.1) +
    theme_minimal() + labs(x = "Individuals", title = title, y = "Ancestry", fill = "Populations") +
    scale_y_continuous(expand = c(0, 0)) +
    scale_x_discrete(expand = expand_scale(add = 1)) +
    theme(panel.spacing.x = unit(0.1, "lines"),
      axis.text.x = element_blank(),
      panel.grid = element_blank()
    )
  ggsave(paste(probfile,".png", sep = ""), dpi = 300, units = "cm", width = width, height = height)
}
