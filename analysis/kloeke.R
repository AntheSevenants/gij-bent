library(dplyr)
library(sf) # geographic data
library(ggplot2)
library(ggthemes) # for map theme

# == BE provinces ==
provinces <- st_read(dsn = "../analysis/provinces/Refprv.shp")
provinces <- st_transform(provinces, 4326)

# == NL provinces ==
nl_provinces <- st_read(dsn = "../analysis/nl_provincies/Provincies.shp")
nl_provinces <- st_transform(nl_provinces, 4326)

# Load Kloeke coordinates
kloeke <- read.csv("../analysis/kloeke/kloeke.csv")

# Load Dynasand research dataset
df_gij <- read.delim("../analysis/kloeke/gij_bent.csv", sep=";")
# Turn categories into factors
df_gij$category <- df_gij$category %>% as.factor()

# Remove noise
banned_categories <- names(which(table(df_gij$category) < 10))
df_gij <- df_gij[!df_gij$category %in% banned_categories,]
# Attach Kloeke coordinates
df_gij <- merge(x=df_gij, y=kloeke, 
                by.x="Kloeke", by.y="kloeke_nieuw", all.x=TRUE)
df_gij <- df_gij[!is.na(df_gij$lat),]
# Remove duplicates
df_gij = df_gij[!duplicated(df_gij$Kloeke),]
# Make friendly names
df_gij$category <- gsub("_", " ", df_gij$category)

dynasand_plot <- function() {
  # Create a nice plot
  ggplot() +
    geom_sf(data = provinces$geometry, fill="#ffffcc") +
    geom_sf(data = nl_provinces$geometry, fill="#ffedcc") +
    theme_map() +
    geom_jitter(aes(y=lat, x=lon, shape=category, color=category), data=df_gij) + 
    guides(color=guide_legend(title="Constructie"),
           shape=guide_legend(title="Constructie")) +
    theme(legend.justification = c(0, 1), legend.position = c(0, 1))
}