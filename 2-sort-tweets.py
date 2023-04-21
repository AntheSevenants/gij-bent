import argparse
import json
import re
import pandas as pd

from glob import glob
from pathlib import Path
from tqdm.auto import tqdm

parser = argparse.ArgumentParser(
    description='sort-tweets - convert tweets to TSV and keep only relevant ones')
parser.add_argument('corpus_directory', type=str, help='path to the directory with all retrieved tweets')
parser.add_argument('working_tsv', type=str, help='The TSV which contains all current tweets')

args = parser.parse_args()

jsonl_files = glob(f"{args.corpus_directory}/*.jsonl")
jsonl_files.sort()

good_tweets = []

for jsonl_file in tqdm(jsonl_files, desc="jsonl files"):
    stem = Path(jsonl_file).stem
    if "bent" in stem:
        construction_type = "bent"
    elif "zijt" in stem:
        construction_type = "zijt"
    else:
        raise ValueError("jsonl file found which doesn't correspond to any known construction")
    
    with open(jsonl_file, "rt") as reader:
        for line in reader.readlines():
            tweet = json.loads(line)

            if tweet["place"] is not None:
                if "Bel" in tweet["place"][1]:
                    good_tweets.append((construction_type, tweet))

rows = []
for good_tweet in tqdm(good_tweets, desc="Converting good tweets"):
    construction_type = good_tweet[0]
    tweet = good_tweet[1]

    tweet_dict = {
        "construction_type": construction_type,
        "year": re.findall("^(\d{4})", tweet["date"])[0],
        "date": tweet["date"],
        "content": tweet["content"].replace("\n", " "),
        "id": tweet["id"],
        "user_id": tweet["user_id"],
        "username": tweet["username"].replace("\n", " "),
        "user_display_name": tweet["user_display_name"].replace("\n", " "),
        "url": tweet["url"].replace("\n", " "),
        "user_verified": tweet["user_verified"],
        "year_user_created": re.findall("^(\d{4})", tweet["user_created"])[0],
        "user_followers_count": tweet["user_followers_count"],
        "user_friends_count": tweet["user_friends_count"],
        "user_tweet_count": tweet["user_tweet_count"],
        "user_favourites_count": tweet["user_favourites_count"],
        "user_listed_count": tweet["user_listed_count"],
        "user_media_count": tweet["user_media_count"],
        "user_location": tweet["user_location"].replace("\n", " "),
        "user_profile_image_url": tweet["user_profile_image_url"],
        "reply_count": tweet["reply_count"],
        "retweet_count": tweet["retweet_count"],
        "like_count": tweet["like_count"],
        "quote_count": tweet["quote_count"],
        "source_label": tweet["source_label"].replace("\n", " "),
        #"links": tweet.links,
        "mentioned_users_count": tweet["mentioned_users_count"],
        "lat": tweet["coordinates"][0],
        "long": tweet["coordinates"][0],
        "place_id": tweet["place"][0].replace("\n", " "),
        "place_full_name": tweet["place"][1].replace("\n", " "),
        "place_reported_name": tweet["place"][2].replace("\n", " "),
        "hashtag_count": len(tweet["hashtags"]) if tweet["hashtags"] is not None else 0,
    }

    rows.append(tweet_dict)

df = pd.DataFrame(rows)

df.to_csv(args.working_tsv, sep="\t", index=False)

print(f"Written output to {args.working_tsv}")