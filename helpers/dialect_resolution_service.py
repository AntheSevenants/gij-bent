import json

from shapely.geometry import shape, Point

# https://stackoverflow.com/questions/20776205/point-in-polygon-with-geojson-in-python
class DialectResolutionService:
	def __init__(self, dialects_file, filter_name):
		# Load dialect regions from json
		with open(dialects_file) as file:
			geo_json = json.load(file)

		self.dialects = {}

		# Initialise each dialect region in memory
		for feature in geo_json["features"]:
			dialect = feature["properties"][filter_name]
			self.dialects[dialect] = shape(feature['geometry'])

	def point_to_dialect(self, lat, lng):
		lat = float(lat)
		lng = float(lng)

		# Go over each dialect region and check whether the point falls within the region
		for dialect in self.dialects:
			geo_point = Point(lng, lat)

			if self.dialects[dialect].contains(geo_point):
				return dialect

		# If the dialect wasn't anywhere in our dialect region, the point is probably somewhere in Wallonia
		# So we return False
		return False