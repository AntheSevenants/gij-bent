import json
import datetime
import argparse
import snscrape.modules.twitter as sntwitter
from tqdm.auto import tqdm

parser = argparse.ArgumentParser(
    description='retrieve-tweets - thank you Elon')
parser.add_argument('construction', type=str,
                    help='zijt | bent')
parser.add_argument('year', type=int, help='The year to scrape for')

args = parser.parse_args()

YEAR = str(args.year)

YEAR_SNIPPET = f"since:{YEAR}-01-01 until:{YEAR}-12-31"
GIJ_BENT_QUERY = f"(ge OR gij OR gy bent) OR \"bende gij\" -je -jij {YEAR_SNIPPET} lang:nl"
GIJ_ZIJT_QUERY = f"(ge OR gij OR gy zijt) OR (ge OR gij OR gy zyt) OR (zijde ge OR zijde gij OR zijde gy) OR (zyde ge OR zyde gij OR zyde gy) OR (zedde ge OR zedde gij OR zedde gy) {YEAR_SNIPPET} -je -jij lang:nl"

OUTPUT_FILE = f"output/{args.construction}_{YEAR}.jsonl"

def date_to_string(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def tweet_to_dict(tweet):
    return {
        "url": tweet.url,
        "date": date_to_string(tweet.date),
        "content": tweet.rawContent,
        "id": tweet.id,
        "username": tweet.user.username,
        "user_id": tweet.user.id,
        "user_display_name": tweet.user.displayname,
        "user_description": tweet.user.rawDescription,
        "user_verified": tweet.user.verified,
        "user_created": date_to_string(tweet.user.created),
        "user_followers_count": tweet.user.followersCount,
        "user_friends_count": tweet.user.friendsCount,
        "user_tweet_count": tweet.user.statusesCount,
        "user_favourites_count": tweet.user.favouritesCount,
        "user_listed_count": tweet.user.listedCount,
        "user_media_count": tweet.user.mediaCount,
        "user_location": tweet.user.location,
        "user_profile_image_url": tweet.user.profileImageUrl,
        "reply_count": tweet.replyCount,
        "retweet_count": tweet.retweetCount,
        "retweet_count": tweet.retweetCount,
        "retweet_count": tweet.retweetCount,
        "like_count": tweet.likeCount,
        "quote_count": tweet.quoteCount,
        "source_label": tweet.sourceLabel,
        #"links": tweet.links,
        "mentioned_users_count": len(tweet.mentionedUsers) if tweet.mentionedUsers is not None else 0,
        "coordinates": (tweet.coordinates.latitude, tweet.coordinates.longitude) if tweet.coordinates is not None else None,
        "place": (tweet.place.id, tweet.place.fullName, tweet.place.name) if tweet.place is not None else None,
        "hashtags": tweet.hashtags
    }

QUERY = GIJ_BENT_QUERY if args.construction == "bent" else GIJ_ZIJT_QUERY

with open(OUTPUT_FILE, "at", encoding="UTF-8") as writer:
    for tweet in tqdm(sntwitter.TwitterSearchScraper(QUERY).get_items(), desc=YEAR):
        tweet_dict = tweet_to_dict(tweet)
        tweet_json = json.dumps(tweet_dict)
        writer.write(f"{tweet_json}\n")