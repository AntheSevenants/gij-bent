import time
import pyproj

from shapely.geometry import shape, Point
from geopy.geocoders import Nominatim

geolocator = Nominatim(
    user_agent="Anthe Sevenants dialectology research (anthe.sevenants@kuleuven.be)")

geod = pyproj.Geod(ellps='WGS84')  # used to compute Antwerp distance
antwerp_point = Point(4.780751, 51.321583)


def geolocate(normalised_location):
    tries = 0
    while tries < 10:
        try:
            location = geolocator.geocode(normalised_location)
            break
        except:
            # print("Geocoder exception - waiting 5s")
            tries += 1
            time.sleep(5)
    if location is None:
        return
    # print("Coordinates found")
    lat = float(location.latitude)
    lng = float(location.longitude)

    return lat, lng


def distance_from_antwerp(lat, lng):
    # https://gis.stackexchange.com/a/80905
    angle1, angle2, distance = geod.inv(
        lng, lat, antwerp_point.x, antwerp_point.y)
    distance_from_north_antwerp = round(distance / 1000, 2)

    return distance_from_north_antwerp
