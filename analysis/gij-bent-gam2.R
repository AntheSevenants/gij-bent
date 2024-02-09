library(mgcv) # GAM
library(sf) # geographic data
library(tidyr) # expand_grid
library(ggthemes) # for map theme
library(cowplot) # plot_grid
library(dplyr) # group_by
library(scales) # percent
library(nngeo) # removing the Brussels hole

source("gij-bent2.R")

df_solo <- df %>% one_user_one_tweet()

#
# GAM
#

build_gam <- function(df) {
  fit <- gam(
    construction_type ~ s(long) + s(lat) + te(long, lat),
    data = df,
    family = binomial,
    method = "REML"
  )
  
  return(fit)
}

# Shapefiles

# == Flanders and Wallonia ==
flanders <- st_read(dsn = "regions/régions_08.shp")
brussels <- flanders[flanders$Nom == "Bruxelles-Capitale",] # Bonjour
flanders <-
  flanders[flanders$Nom == "Vlaams Gewest", ] # Wallonia bye
flanders <- st_transform(flanders, 4326) # convert to GPS coordinates system
brussels <- st_transform(brussels, 4326)

# == Noorderkempen area ==
noorderkempen <- st_read("Noorderkempen/POLYGON.shp")
noorderkempen <- st_transform(noorderkempen, 4326)

noorderkempen <- st_intersection(flanders, noorderkempen)

# == Dialect area borders ==
dialects <- st_read("dialects/POLYGON.shp")
dialects <- st_transform(dialects, 4326)

# == Municipalities ==
gemeenten <- st_read("gemeenten/Refgem.shp")
gemeenten <- st_transform(gemeenten, 4326)
# Remove superfluous data
keep_columns <- c("NAAM", "geometry")
gemeenten <- subset(gemeenten, select = keep_columns)
# Prepare Brussels for a merger
# (lol, this is not a political statement I promise)
brussels$NAAM <- c("Brussel")
brussels <- subset(brussels, select = keep_columns)
# Merger! Don't tell the Flemish nationalists
gemeenten <- rbind(gemeenten, brussels)

# Read the postal codes dataset
df_zip <- read.csv("data/zipcode-belgium.csv",
                   header=FALSE,
                   col.names = c("zip", "name", "long", "lat"))
df_zip$key = tolower(df_zip$name)

gemeenten$key = tolower(gemeenten$NAAM)

# Attach zip codes to the map
gemeenten <- merge(x = gemeenten, y = df_zip, by="key", all.x=TRUE)

# == Provinces ==
provinces <- st_read("gemeenten/Refprv.shp")
provinces <- st_transform(provinces, 4326)
plot(provinces$geometry)
provinces <- subset(provinces, select = keep_columns)

brabant <- provinces[provinces$NAAM == "Vlaams Brabant",]
plot(brabant$geometry)
antwerpen <- provinces[provinces$NAAM == "Antwerpen",]
plot(antwerpen$geometry)
groot_brabant <- st_union(brabant, antwerpen)
plot(groot_brabant$geometry)
groot_brabant <- st_remove_holes(groot_brabant)
groot_brabant <- subset(groot_brabant,
                        select = keep_columns)
groot_brabant$NAAM <- c("Brabant")

provinces <- rbind(provinces, groot_brabant)
provinces <- provinces[!(provinces$NAAM %in% c("Vlaams Brabant", "Antwerpen")),]

# Predictions
# We generate data points to make the tile plot
# The more points, the higher resolution the plot will be

logit2prob <- function(logit){
  odds <- exp(logit)
  prob <- odds / (1 + odds)
  return(prob)
}

predict_coords <- function(df, fit) {
  long_from <- min(df$long) - 0.015
  long_to <- max(df$long) + 0.1
  
  lat_from <- min(df$lat)
  lat_to <- max(df$lat) + 0.05
  
  df_pred <- expand_grid(
    long = seq(
      from = long_from,
      to = long_to,
      length.out = 100
    ),
    lat = seq(
      from = lat_from,
      to = lat_to,
      length.out = 100
    )
  )
  
  # Turn into dataframe
  df_pred <- predict(fit, newdata = df_pred,
                     se.fit = TRUE) %>%
    as_tibble() %>%
    cbind(df_pred)
  
  df_pred$prob <- logit2prob(df_pred$fit)
  
  return(df_pred)
}

plot_map <- function(df_pred, gemeenten) {
  # The mighty plot!
  # Do not be surprised if it takes around a minute to generate this plot
  # Tiling the 10.000 predictions is a tough job!
  # color=alpha(gemeenten$value, 0.4),
  ggplot() +
    theme_map() +
    #theme(legend.position = "none") +
    geom_sf(
      data = gemeenten$geometry,
      aes(fill = gemeenten$prob,
          color = gemeenten$prob > 0.5),
    ) +
    scale_fill_distiller(palette = "YlGnBu",
                         labels = scales::label_percent(),
                         limits = c(0, 1)) +
    scale_color_manual(values = c("white", "#323232"),
                       guide = "none") +
    #geom_sf(data=provinces$geometry, fill="transparent", color=alpha("#c16465", 0.8)) +
    geom_sf(
      data = noorderkempen$geometry,
      color = "#c16465",
      linewidth = 0.5,
      fill = "transparent"
    ) +
    geom_sf(
      data = provinces$geometry,
      color = "#c16465",
      linewidth = 0.5,
      fill = "transparent"
    ) +
    geom_sf_text(
      data = gemeenten$geometry,
      check_overlap=T,
      size=2,
      aes(label = gemeenten$zip,
          color = gemeenten$prob > 0.5)) +
    #geom_jitter(data = df, width=0.02, height=0.02, aes(x=long, y=lat, color=df$construction_type)) +
    coord_sf(default_crs = sf::st_crs(4326)) +
    guides(fill=guide_legend(title="Kans op 'gij bent'")) +
    theme(legend.position = "bottom", legend.margin=margin(c(0,0,0,45)))
}

nearest_point <- function(df_pred, lat, long, column) {
  # We supply the lat long coordinates to define ap point
  point <- st_point(c(long, lat)) %>% st_sfc(crs = 4326)
  
  point_index <- st_nearest_feature(point, df_pred, longlat=TRUE)
  
  #return(point_index)
  return(df_pred[point_index,][[column]])
}

df_to_plot <- function(df, too.far=NA) {
  df_pred <- df %>%
    one_user_one_tweet() %>%
    build_gam() %>%
    predict_coords(df, .)
  
  coords <- df_pred %>% st_as_sf(coords = c("long", "lat"), crs=4326)
  
  # Copy gemeenten
  gemeenten_ <- gemeenten
  
  # For each town, we want to compute the closest point
  # From that point, we can get the prediction for that town
  # And like that, we can make a nice map :)
  
  gemeenten_$prob <- apply(gemeenten_, 1, function(row) {
    nearest_point(coords, row$lat, row$long, "prob")
  })
  
  if (!is.na(too.far)) {
    too_far <-
      exclude.too.far(df_pred$long, df_pred$lat, df$long, df$lat, too.far)
  } else {
    too_far <- rep(FALSE, df_pred$long %>% length)
  }
  
  # Remove "too far" data points
  df_pred$too_far <- too_far
  df_pred <- df_pred[!df_pred$too_far,]
  
  plot_map(df_pred, gemeenten_)
}

fit <- build_gam(df_solo)

tiff(filename="../paper/figuren/figuur_7.tiff", width=15, height=10, units="cm", res=300)
df_to_plot(df_solo)
dev.off()

png(filename="../paper/figuren/figuur_7.png", width=15, height=10, units="cm", res=300)
df_to_plot(df_solo)
dev.off()
