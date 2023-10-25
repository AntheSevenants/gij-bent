library(mgcv) # GAM
library(sf) # geographic data
library(tidyr) # expand_grid
library(ggthemes) # for map theme
library(cowplot) # plot_grid
library(dplyr) # group_by
library(scales) # percent

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

fit <- build_gam(df_solo)

# What does the model look like?
fit

summary(fit)

# Generate a preliminary heatmap
vis.gam(
  fit,
  view = c("long", "lat"),
  plot.type = "contour",
  color = "heat"
)

# Shapefiles

# == Flanders ==
flanders <- st_read(dsn = "regions/régions_08.shp")
flanders <-
  flanders[flanders$Nom == "Vlaams Gewest", ] # Wallonia bye
plot(flanders$geometry) # plot the geometry column (does Flanders show?)

# Bounding box, needed for plotting the negative white overlay
# The negative white overlay will be used to cover the excess data generated
# by the GAM predictions
bounding_box <- st_bbox(flanders)
bounding_box["xmin"] <- bounding_box["xmin"] - 1500
bounding_box["xmax"] <- bounding_box["xmax"] + 1500
bounding_box["ymin"] <- bounding_box["ymin"] - 1500
bounding_box["ymax"] <- bounding_box["ymax"] + 4000

# Turn the bounding box into geometry
bounding_box <- bounding_box %>%
  st_as_sfc() %>%
  st_as_sf()

# Now, subtract Flanders from the bounding box
# We end up with a box with a Flanders-shaped hole
mask <- st_difference(bounding_box, flanders)
mask_coords = st_transform(mask, 4326) # convert to GPS coordinates system

# == Noorderkempen area ==
noorderkempen <- st_read("Noorderkempen/POLYGON.shp")
noorderkempen <- st_transform(noorderkempen, 4326)

# == Dialect area borders ==
dialects <- st_read("dialects/POLYGON.shp")
dialects <- st_transform(dialects, 4326)

# == Municipalities ==
gemeenten <- st_read("gemeenten/Refgem.shp")
gemeenten <- st_transform(gemeenten, 4326)
plot(gemeenten$geometry)

# == Provincies ==
provinces <- st_read("gemeenten/Refprv.shp")
provinces <- st_transform(provinces, 4326)
plot(provinces$geometry)

# Predictions
# We generate data points to make the tile plot
# The more points, the higher resolution the plot will be

logit2prob <- function(logit){
  odds <- exp(logit)
  prob <- odds / (1 + odds)
  return(prob)
}

predict_coords <- function(fit) {
  long_from <- min(df_solo$long) - 0.015
  long_to <- max(df_solo$long) + 0.1
  
  lat_from <- min(df_solo$lat)
  lat_to <- max(df_solo$lat) + 0.05
  
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

plot_map <- function(df_pred) {
  # The mighty plot!
  # Do not be surprised if it takes around a minute to generate this plot
  # Tiling the 10.000 predictions is a tough job!
  # color=alpha(gemeenten$value, 0.4),
  ggplot() +
    geom_sf(data = flanders$geometry) +
    theme_map() +
    #theme(legend.position = "none") +
    geom_tile(data = df_pred, aes(x = long, y = lat, fill = prob)) +
    scale_fill_distiller(palette = "YlGnBu", labels = scales::label_percent()) +
    geom_sf(
      data = gemeenten$geometry,
      fill = "transparent",
      color = alpha("#c16465", 0.2)
    ) +
    #geom_sf(data=provinces$geometry, fill="transparent", color=alpha("#c16465", 0.8)) +
    geom_sf(
      data = noorderkempen$geometry,
      color = "#c16465",
      linewidth = 1,
      fill = "transparent"
    ) +
    geom_sf(
      data = dialects$geometry,
      color = "#c16465",
      linewidth = 1,
      fill = "transparent"
    ) +
    geom_contour(data = df_pred,
                 aes(x = long, y = lat, z = prob),
                 colour = "white") +
    geom_sf(data = mask,
            fill = 'white',
            color = "white") +
    #geom_jitter(data = df, width=0.02, height=0.02, aes(x=long, y=lat, color=df$construction_type)) +
    coord_sf(default_crs = sf::st_crs(4326)) +
    guides(fill=guide_legend(title="Kans op 'gij bent'")) +
    theme(legend.position = "bottom", legend.margin=margin(c(0,0,0,45)))
}

df_to_plot <- function(df, too.far=NA) {
  df_pred <- df %>%
    one_user_one_tweet() %>%
    build_gam() %>%
    predict_coords()
  
  if (!is.na(too.far)) {
    too_far <-
      exclude.too.far(df_pred$long, df_pred$lat, df$long, df$lat, too.far)
  } else {
    too_far <- rep(FALSE, df_pred$long %>% length)
  }
  
  # Remove "too far" data points
  df_pred$too_far <- too_far
  df_pred <- df_pred[!df_pred$too_far,]
  
  df_pred %>% plot_map()
}

tiff(filename="../paper/figuren/figuur_7.tiff", width=15, height=10, units="cm", res=300)
df_to_plot(df_solo)
dev.off()

png(filename="../paper/figuren/figuur_7.png", width=15, height=10, units="cm", res=300)
df_to_plot(df_solo)
dev.off()
