library(sf) # geographic data
library(ggplot2) # for plots
library(ggthemes) # for map theme

# == Flanders ==
flanders <- st_read(dsn = "../analysis/regions/régions_08.shp")
flanders <-
  flanders[flanders$Nom == "Vlaams Gewest", ] # Wallonia bye
flanders <- st_transform(flanders, 4326)

# == Provinces ==
provinces <- st_read(dsn = "../analysis/provinces/Refprv.shp")
provinces <- st_transform(provinces, 4326)
plot(provinces$geometry)

# == Noorderkempen area ==
noorderkempen <- st_read("../analysis/Noorderkempen/POLYGON.shp")
noorderkempen <- st_transform(noorderkempen, 4326)

diff <- st_intersection(noorderkempen, flanders)

province_plot <- function() {
  
ggplot() +
  geom_sf(data = flanders$geometry) +
  geom_sf(data = provinces$geometry) +
  theme_map() +
  theme(legend.position = "none") +
  geom_sf(
    data = diff$geometry,
    color = "#c16465",
    linewidth = 0.5,
    fill = "transparent"
  ) +
  geom_point(aes(y=51.321583, x=4.780751)) +
  annotate("text", y=51.181583, x=4.740751, label="Antwerpen", color="#4f4f4f", size=3) +
  annotate("text", y=50.881583, x=4.740751, label="Vlaams-Brabant", color="#4f4f4f", size=3) +
  annotate("text", y=51.0, x=5.440751, label="Limburg", color="#4f4f4f", size=3) +
  annotate("text", y=51.03, x=3.800751, label="Oost-Vlaanderen", color="#4f4f4f", size=3) +
  annotate("text", y=51.03, x=3.000751, label="West-Vlaanderen", color="#4f4f4f", size=3)
}