library(ggplot2) # plots
library(magrittr) # %>% pipes
library(forcats) # collapse factor

# We read the dataset
df <- read.delim("../tweets_geo.tsv")

# Make sure the factor levels are set up so *bent* is the non-default level
df$construction_type <- factor(df$construction_type, levels=c("zijt", "bent"))

# Turn dialect into a factor
df$dialect <- factor(df$dialect)

# Turn context into a factor
df$context <- factor(df$context, levels=c("main", "inversion", "other"))

# Turn emotion into a factor
df$emotion <- factor(df$emotion)
df$emotion <- df$emotion %>% 
                fct_collapse("emotion" = c("fear", "joy", "sadness", "anger"))
df$emotion <- factor(df$emotion, levels=c("neutral", "emotion"))

# Turn gender into a factor, male = reference
df$gender <- factor(df$gender, levels=c("male", "female", ""))

# If a user is mentioned in the tweet, we consider it a "reply"
df$is_reply <- df$mentioned_users_count > 0
# Has to be turned into a factor to work in some plots
df$is_reply <- as.factor(df$is_reply)

# Remove worthless Twitter coordinates and replace with my own
df <- df[ , -which(names(df) %in% c("lat","long"))]
colnames(df)[colnames(df) == "norm_lat"] <- "lat"
colnames(df)[colnames(df) == "norm_long"] <- "long"

# Only one tweet per user
one_user_one_tweet <- function(df) {
  df[!duplicated(df$user_id),]
}


