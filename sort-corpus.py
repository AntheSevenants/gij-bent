import os
import shutil
import re

from lxml import etree, html
from io import StringIO, BytesIO
from pattern.nl import sentiment
from langdetect import detect
from geopy.geocoders import Nominatim

CORPUS_DIRECTORY = "corpus"

geolocator = Nominatim(user_agent="Anthe Sevenants corpus linguistics research (anthe.sevenants@student.kuleuven.be)")

class CsvWriter:
	def __init__(self, filename):
		self.output_filename = "corpus/" + os.path.basename(filename).replace(".xml", ".csv")

		with open(self.output_filename, "w", encoding='utf8') as csv_file:
			csv_file.write("tweet_text;dialect;is_reply;polarity;construction_type\n")

		print("CSV header written")

	def write_tweet(self, tweet_text, dialect, is_reply, polarity, construction_type):
		# As per the CSV spec, you need to escape " as ""
		tweet_text = tweet_text.replace("\"", "\"\"")

		with open(self.output_filename, "a", encoding='utf8') as csv_file:
			csv_file.write("\"{}\";{};{};{};{}\n".format(tweet_text,
													   dialect,
													   is_reply,
													   polarity,
													   construction_type))

		print("Tweet written to file")

class TweetCorpus:
	def __init__(self, filename):
		print("Initialising corpus: {}".format(filename))
		parser = etree.HTMLParser(encoding="utf-8")
		root = html.parse(filename, parser=parser)
		# Find all tweet nodes
		self.tweets = root.findall("//tweet")
		self.csv_writer = CsvWriter(filename)

	def convert_tweets(self):
		for tweet in self.tweets:
			# We can check whether this tweet comes from Belgium by using the normalised location attribute
			# Reject if tweet does not come from Belgium (sorry Dutchies)
			if not "Belgium" in tweet.attrib["norm_loc"]:
				continue
	
			# Extract tweet from element
			tweet_text = tweet.text
	
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
			# If nothing is found, we reject the tweet altogether
			if re.search(r'\bzijt\b', tweet_text, re.IGNORECASE) is not None:
				construction_type = "zijt"
				#print("ZIJT is found")
			elif re.search(r'\bbent\b', tweet_text, re.IGNORECASE) is not None:
				construction_type = "bent"
				#print("BENT is found")
			else:
				continue
	
			# Detect the language of this tweet
			#try:
			#	language = detect(tweet_text)
			## I've deduced from testing that if language detecting fails, there is no actual language to be found
			## in the tweet (consists only of smiley faces etc.), so we can safely reject this tweet
			#except:
			#	continue
#	
			## Sometimes, the library returns 'Afrikaans' for Dutch tweets
			## I don't think we have any Afrikaans data here, so I accept both languages
			## If the language of the tweet is not Dutch, reject this tweet
			#if not language in ["nl", "af"]:
			#	continue
	
			# If by chance there are no latlong values for this tweet, we have to reject the tweet
			# because we cannot be sure where it comes from
			if not "lat" in tweet.attrib or not "lng" in tweet.attrib:
				continue
		
			# I need to find the province from where a tweet was posted to assume the location of the tweeter
			# I use a latlong resolution service to get the address (which includes the province)
			# Later, we sort this into the dialect areas we want
			# I don't use norm_loc because it doesn't give province information
			location = geolocator.reverse("{}, {}".format(tweet.attrib["lat"], tweet.attrib["lng"]))			
			location = location.raw

			dialect = "NA"
			if location["address"]["state"] in [ "West-Vlaanderen", "Oost-Vlaanderen" ]:
				dialect = "Vlaams"
			elif location["address"]["state"] in [ "Vlaams-Brabant", "Antwerpen", "Région de Bruxelles-Capitale - Brussels Hoofdstedelijk Gewest" ]:
				dialect = "Brabants"
			elif location["address"]["state"] in [ "Limburg" ]:
				dialect = "Limburgs"
			else:
				continue
		
			# All Twitter replies start with @
			is_reply = tweet_text[0] == "@"
	
			# Sentiment analysis
			polarity = sentiment(tweet_text)[0]
	

			self.csv_writer.write_tweet(tweet_text, dialect, is_reply, polarity, construction_type)

# Get all the corpus files
tweet_files = os.listdir("tweets")

# Reset the corpus directory
if os.path.exists(CORPUS_DIRECTORY):
	shutil.rmtree(CORPUS_DIRECTORY)
os.mkdir(CORPUS_DIRECTORY)

for tweet_file in tweet_files:
	TweetCorpus("tweets/" + tweet_file).convert_tweets()
