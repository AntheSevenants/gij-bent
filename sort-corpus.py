import os
import shutil
import re
import math

from glob import glob
from tqdm.auto import tqdm

from lxml import etree, html
from geopy.geocoders import Nominatim
import pyproj
import json
from shapely.geometry import shape, Point

import time

CORPUS_DIRECTORY = "corpus"

geolocator = Nominatim(user_agent="Anthe Sevenants corpus linguistics research (anthe.sevenants@student.kuleuven.be)")
geod = pyproj.Geod(ellps='WGS84') # used to compute Antwerp distance
antwerp_point = Point(4.780751, 51.321583)

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

class CsvWriter:
	def __init__(self, filename):
		self.output_filename = "corpus/{}.csv".format(os.path.basename(filename).replace(".xml", ""))

		with open(self.output_filename, "w", encoding='utf8') as csv_file:
			csv_file.write("tweet_text;username;dialect;is_reply;distance_from_north_antwerp;construction_type\n")

		#print("CSV header written")

	def write_tweet(self, tweet_text, username, dialect, is_reply, distance_from_north_antwerp, construction_type):
		# As per the CSV spec, you need to escape " as ""
		tweet_text = tweet_text.replace("\"", "\"\"")

		with open(self.output_filename, "a", encoding='utf8') as csv_file:
			csv_file.write("\"{}\";{};{};{};{};{}\n".format(tweet_text,
													   username,
													   dialect,
													   is_reply,
													   distance_from_north_antwerp,
													   construction_type))

		#print("Tweet written to file")

class TweetCorpus:
	def __init__(self, filename, csv_writer_zijt, csv_writer_bent, dialect_resolution):
		#print("Initialising corpus: {}".format(filename))
		parser = etree.HTMLParser(encoding="utf-8")
		root = html.parse(filename, parser=parser)
		# Find all tweet nodes
		self.tweets = root.findall("//tweet")
		# Define both 'zijt' and 'bent' writers (will go into separate files)
		self.csv_writer_zijt = csv_writer_zijt
		self.csv_writer_bent = csv_writer_bent

		self.dialect_resolution = dialect_resolution

	def convert_tweets(self):
		for tweet in tqdm(self.tweets, leave=False):
			# We can check whether this tweet comes from Belgium by using the normalised location attribute
			# Reject if tweet does not come from Belgium (sorry Dutchies)
			if not "Belgium" in tweet.attrib["norm_loc"]:
				continue
	
			# Extract tweet from element
			tweet_text = tweet.text

			# Some parts of the corpus are broken so we have to find out whether the tweet is "legal" or not
			if type(tweet_text) != str:
				#print("Broken tweet")
				continue

			username = tweet.attrib["user"]
	
			# Remove URLs from tweet (we aren't interested in them)
			tweet_text = re.sub(r'https?:\/\/.*\b', '', tweet_text).strip()
	
			# If a tweet consisted of only links, tweet length will be zero (and we will have to reject the tweet)
			if len(tweet_text) == 0:
				continue
	
			# If we cannot find the pronominal "ge" or "gij" in the tweet, we have to discard it
			if re.search(r'\b(ge*|gi*j*|gy*)\b', tweet_text, re.IGNORECASE) is None:
				continue
	
			#print("GE is found!")
	
			construction_type = None
			# Here we find out whether the construction is "ge bent" or "ge zijt" (will be reviewed by a human later)
			# We assign the correct csv writer object as well
			# If nothing is found, we reject the tweet altogether
			if re.search(r'\b(zi*j+|zy+|z[eéè][td]?)', tweet_text, re.IGNORECASE) is not None:
				construction_type = "zijt"
				csv_writer = self.csv_writer_zijt
				#print("ZIJT is found")
			elif re.search(r'\bben[td]', tweet_text, re.IGNORECASE) is not None:
				construction_type = "bent"
				csv_writer = self.csv_writer_bent
				#print("BENT is found")
			else:
				continue

			# If there are no latlong values for this tweet, we have to find the coordinates ourselves
			# because we need the coordinates to find the dialect region
			if not "lat" in tweet.attrib or not "lng" in tweet.attrib:
				#print("No latlong found, looking up coordinates")

				tries = 0
				while tries < 10:
					try:
						location = geolocator.geocode(tweet.attrib["norm_loc"])
						break
					except:
						print("Geocoder exception - waiting 5s")
						tries += 1
						time.sleep(5)

				if location is None:
					return

				#print("Coordinates found")
				lat = float(location.latitude)
				lng = float(location.longitude)
			# If there are coordinates, we can just take them from the metadata of the tweet
			else:
				lat = float(tweet.attrib["lat"])
				lng = float(tweet.attrib["lng"])

			dialect = self.dialect_resolution.point_to_dialect(lat, lng)
			#print(dialect)
			if not dialect:
				continue

			# https://gis.stackexchange.com/a/80905
			angle1, angle2, distance = geod.inv(lng, lat, antwerp_point.x, antwerp_point.y)
			distance_from_north_antwerp = round(distance / 1000, 2)
			#print(distance_from_north_antwerp)
			#distance_from_north_antwerp = math.log(distance_from_north_antwerp * 100)
		
			# All Twitter replies start with @
			is_reply = tweet_text[0] == "@"
	
			csv_writer.write_tweet(tweet_text, username, dialect, is_reply, distance_from_north_antwerp, construction_type)

# Get all the corpus files
tweet_files = glob("tweets/*.xml")

# Reset the corpus directory
if os.path.exists(CORPUS_DIRECTORY):
	shutil.rmtree(CORPUS_DIRECTORY)
os.mkdir(CORPUS_DIRECTORY)

dialect_resolution = DialectResolutionService("dialects.json", "dialect")

csv_writer_zijt = CsvWriter("corpus_zijt")
csv_write_bent = CsvWriter("corpus_bent")

for tweet_file in tqdm(tweet_files):
	TweetCorpus(tweet_file, csv_writer_zijt, csv_write_bent, dialect_resolution).convert_tweets()
