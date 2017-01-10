#!/usr/bin/env Rscript

library(lsr)
library(methods)

# General Functions =================================================

# Calculate confidence interval from a t distribution
# Returns the size of the interval around the mean of `data`
ci.t <- function(data, alpha = 0.05) {
  qt(1 - (alpha / 2), df = length(data) - 1) * sd(data) / sqrt(length(data))
}

# Main ==============================================================

# Read the data file (first command line argument)
args <- commandArgs(TRUE)
data <- read.table(args, header=TRUE, sep='\t')

# Convert some numeric fields into factors
data$subject <- factor(data$subject)

condition.summary <- function(data.condition, a_name, b_name) {
  N <- nrow(data.condition)
  data.A <- data.condition$a_t
  data.B <- data.condition$b_t
  mean.A <- mean(data.A)
  mean.B <- mean(data.B)
  pref.A <- sum(data.condition$pref == 'A')
  pref.B <- sum(data.condition$pref == 'B')

  rating.A <- data.condition$a_r
  rating.B <- data.condition$b_r

  first.A <- sum(data.condition$first == 'A')
  first.B <- sum(data.condition$first == 'B')

  pref.first <- sum(data.condition$first == data.condition$pref)
  pref.second <- sum(data.condition$first != data.condition$pref)

  pref.first.A <- sum(data.condition$first == 'A' & data.condition$pref == 'A')
  pref.second.A <- sum(data.condition$first == 'B' & data.condition$pref == 'A')
  
  pref.first.B <- sum(data.condition$first == 'B' & data.condition$pref == 'B')
  pref.second.B <- sum(data.condition$first == 'A' & data.condition$pref == 'B')

  cat('  A: ', a_name, '\n')
  cat('              Time Mean: ', mean.A, '  CI: ', mean.A - ci.t(data.A), ', ', mean.A + ci.t(data.A), '\n')
  cat('            Rating Mean: ', mean(rating.A), '  Median: ', median(rating.A), '  SD: ', sd(rating.A), '\n')
  cat('      Overall Preferred: ', pref.A, ' / ', N, ' (', pref.A/N*100, '%)\n')
  cat('              Did First: ', first.A, ' / ', N, ' (', first.A/N*100, '%)\n')
  cat('    First and Preferred: ', pref.first.A, ' / ', first.A, ' (', pref.first.A/first.A*100, '%)\n')
  cat('   Second and Preferred: ', pref.second.A, ' / ', first.B, ' (', pref.second.A/first.B*100, '%)\n')

  cat('\n')
  cat('  B: ', b_name, '\n')
  cat('              Time Mean: ', mean.B, '  CI: ', mean.B - ci.t(data.B), ', ', mean.B + ci.t(data.B), '\n')
  cat('            Rating Mean: ', mean(rating.B), '  Median: ', median(rating.B), '  SD: ', sd(rating.B), '\n')
  cat('      Overall Preferred: ', pref.B, ' / ', N, ' (', pref.B/N*100, '%)\n')
  cat('              Did First: ', first.B, ' / ', N, ' (', first.B/N*100, '%)\n')
  cat('    First and Preferred: ', pref.first.B, ' / ', first.B, ' (', pref.first.B/first.B*100, '%)\n')
  cat('   Second and Preferred: ', pref.second.B, ' / ', first.A, ' (', pref.second.B/first.A*100, '%)\n')

  cat('\n')
  cat('    Preferred first: ', pref.first, '\n')
  cat('   Preferred second: ', pref.second, '\n')

  cat('\n')
  cat('Time t-test --------------------------------------------------')
  print(t.test(data.A, data.B, paired=TRUE))
  cat('  d: ', cohensD(data.A, data.B), '\n')

  cat('\n')
  cat('Rating Wilcoxon test -----------------------------------------')
  print(wilcox.test(rating.A, rating.B, paired=T, exact=F))

  cat('\n')
  cat('Preference binomial sign test --------------------------------')
  print(binom.test(pref.A, pref.A + pref.B))

  cat('\n')
  cat('Preference by Order proportion test --------------------------')
  print(prop.test(c(pref.first.A, pref.second.A), c(first.A, first.B)))
}

print('NEUTRAL VS. POSITIVE =========================================')
data.condition <- subset(data, condition=='ControlP')
condition.summary(data.condition, 'Positive', 'Neutral')
       
print('NEUTRAL VS. NEGATIVE =========================================')
data.condition <- subset(data, condition=='ControlN')
condition.summary(data.condition, 'Neutral', 'Negative')
      
print('+END VS. +START ==============================================')
data.condition <- subset(data, condition=='+EndStart')
condition.summary(data.condition, '+End', '+Start')
      
print('+END VS. +MID ==============================================')
data.condition <- subset(data, condition=='+EndMid')
condition.summary(data.condition, '+End', '+Mid')

print('+START VS. +MID ==============================================')
data.condition <- subset(data, condition=='+StartMid')
condition.summary(data.condition, '+Start', '+Mid')

print('-START VS. -END ==============================================')
data.condition <- subset(data, condition=='-StartEnd')
condition.summary(data.condition, '-Start', '-End')

print('-MID VS. -END ==============================================')
data.condition <- subset(data, condition=='-EndMid')
condition.summary(data.condition, '-Mid', '-End')

print('-MID VS. -START ==============================================')
data.condition <- subset(data, condition=='-StartMid')
condition.summary(data.condition, '-Mid', '-Start')
