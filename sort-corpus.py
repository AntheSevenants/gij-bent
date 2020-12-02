import os
import shutil
import re
import math

from lxml import etree, html
from io import StringIO, BytesIO
from pattern.nl import sentiment
from langdetect import detect
from geopy.geocoders import Nominatim

import json
from shapely.geometry import shape, Point

CORPUS_DIRECTORY = "corpus"

geolocator = Nominatim(user_agent="Anthe Sevenants corpus linguistics research (anthe.sevenants@student.kuleuven.be)")

# https://stackoverflow.com/questions/20776205/point-in-polygon-with-geojson-in-python
class DialectResolutionService:
	def __init__(self, dialects_file, filter_name):
		with open(dialects_file) as file:
			geo_json = json.load(file)

		self.dialects = {}

		for feature in geo_json["features"]:
			dialect = feature["properties"][filter_name]
			self.dialects[dialect] = shape(feature['geometry'])

		print(self.dialects)

	def point_to_dialect(self, lat, lng):
		lat = float(lat)
		lng = float(lng)

		print(lat, lng)
		for dialect in self.dialects:
			geo_point = Point(lng, lat)

			if self.dialects[dialect].contains(geo_point):
				return dialect

		# If the dialect wasn't anywhere in our dialect region, something must have gone wrong so we return False
		return False

class CsvWriter:
	def __init__(self, filename):
		self.output_filename = "corpus/{}.csv".format(os.path.basename(filename).replace(".xml", ""))

		with open(self.output_filename, "w", encoding='utf8') as csv_file:
			csv_file.write("tweet_text;username;dialect;is_reply;polarity;distance_from_north_antwerp;construction_type\n")

		print("CSV header written")

	def write_tweet(self, tweet_text, username, dialect, is_reply, polarity, distance_from_north_antwerp, construction_type):
		# As per the CSV spec, you need to escape " as ""
		tweet_text = tweet_text.replace("\"", "\"\"")

		with open(self.output_filename, "a", encoding='utf8') as csv_file:
			csv_file.write("\"{}\";{};{};{};{};{};{}\n".format(tweet_text,
													   username,
													   dialect,
													   is_reply,
													   polarity,
													   distance_from_north_antwerp,
													   construction_type))

		print("Tweet written to file")

class TweetCorpus:
	def __init__(self, filename, csv_writer_zijt, csv_writer_bent, dialect_resolution):
		print("Initialising corpus: {}".format(filename))
		parser = etree.HTMLParser(encoding="utf-8")
		root = html.parse(filename, parser=parser)
		# Find all tweet nodes
		self.tweets = root.findall("//tweet")
		# Define both 'zijt' and 'bent' writers (will go into separate files)
		self.csv_writer_zijt = csv_writer_zijt
		self.csv_writer_bent = csv_writer_bent

		self.dialect_resolution = dialect_resolution

	def convert_tweets(self):
		for tweet in self.tweets:
			# We can check whether this tweet comes from Belgium by using the normalised location attribute
			# Reject if tweet does not come from Belgium (sorry Dutchies)
			if not "Belgium" in tweet.attrib["norm_loc"]:
				continue
	
			# Extract tweet from element
			tweet_text = tweet.text

			# Some parts of the corpus are broken so we have to find out whether the tweet is "legal" or not
			if type(tweet_text) != str:
				print("Broken tweet")
				continue

			username = tweet.attrib["user"]
	
			# Remove URLs from tweet (we aren't interested in them)
			tweet_text = re.sub(r'https?:\/\/.*\b', '', tweet_text).strip()
	
			# If a tweet consisted of only links, tweet length will be zero (and we will have to reject the tweet)
			if len(tweet_text) == 0:
				continue
	
			# If we cannot find the pronominal "ge" or "gij" in the tweet, we have to discard it
			if re.search(r'\b(ge*|gij*|gy*)\b', tweet_text, re.IGNORECASE) is None:
				continue
	
			#print("GE is found!")
	
			construction_type = None
			# Here we find out whether the construction is "ge bent" or "ge zijt" (will be reviewed by a human later)
			# We assign the correct csv writer object as well
			# If nothing is found, we reject the tweet altogether
			if re.search(r'\b(zijt|zyt)\b', tweet_text, re.IGNORECASE) is not None:
				construction_type = "zijt"
				csv_writer = self.csv_writer_zijt
				#print("ZIJT is found")
			elif re.search(r'\bbent\b', tweet_text, re.IGNORECASE) is not None:
				construction_type = "bent"
				csv_writer = self.csv_writer_bent
				#print("BENT is found")
			else:
				continue

			# If by chance there are no latlong values for this tweet, we have to reject the tweet
			# because we cannot be sure where it comes from
			if not "lat" in tweet.attrib or not "lng" in tweet.attrib:
				continue
		
			lat = float(tweet.attrib["lat"])
			lng = float(tweet.attrib["lng"])

			dialect = self.dialect_resolution.point_to_dialect(lat, lng)
			print(dialect)
			if not dialect:
				continue

			distance_from_north_antwerp = Point(lng, lat).distance(Point(4.780751, 51.321583))
			print(distance_from_north_antwerp)
			distance_from_north_antwerp = math.log(distance_from_north_antwerp * 100)
		
			# All Twitter replies start with @
			is_reply = tweet_text[0] == "@"
	
			# Sentiment analysis
			polarity = math.fabs(sum(sentiment(tweet_text)) / 2)
	
			csv_writer.write_tweet(tweet_text, username, dialect, is_reply, polarity, distance_from_north_antwerp, construction_type)

# Get all the corpus files
tweet_files = os.listdir("tweets")

# Reset the corpus directory
if os.path.exists(CORPUS_DIRECTORY):
	shutil.rmtree(CORPUS_DIRECTORY)
os.mkdir(CORPUS_DIRECTORY)

dialect_resolution = DialectResolutionService("dialects.json", "dialect")

csv_writer_zijt = CsvWriter("corpus_zijt")
csv_write_bent = CsvWriter("corpus_bent")

for tweet_file in tweet_files:
	TweetCorpus("tweets/" + tweet_file, csv_writer_zijt, csv_write_bent, dialect_resolution).convert_tweets()
