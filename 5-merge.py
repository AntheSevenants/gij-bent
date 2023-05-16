import argparse
import pandas as pd

parser = argparse.ArgumentParser(
    description='geoguess - provide latlong and dialect area information for each tweet')
parser.add_argument('working_tsv', type=str,
                    help='The TSV which contains all current tweets')
parser.add_argument('geo_tsv', type=str,
                    help='The TSV which contains all geo information')
parser.add_argument('gender_tsv', type=str,
                    help='The TSV which contains all gender information')
parser.add_argument('distance_tsv', type=str,
                    help='The TSV which contains all distance information')
parser.add_argument('--output_tsv', type=str, default="tweets_geo.tsv",
                    help='The TSV to output the merged files to')

args = parser.parse_args()

# Read all dataframes
df_tweets = pd.read_csv(args.working_tsv, sep="\t")
df_geo = pd.read_csv(args.geo_tsv, sep="\t")
df_gender = pd.read_csv(args.gender_tsv, sep="\t")
df_distance = pd.read_csv(args.distance_tsv, sep="\t")

# "lat" and "long" also exist in the Twitter data
# so I provide new names for them before merging
df_geo = df_geo.rename(columns={"lat": "norm_lat", "long": "norm_long"})

# Remove duplicates
df_tweets = df_tweets.drop_duplicates(["id", "user_id"])
df_geo = df_geo.drop_duplicates(["id", "user_id"])
df_distance = df_distance.drop_duplicates(["id", "user_id"])

# join
df_tweets_geo = pd.merge(df_tweets, df_geo, on=["id", "user_id"], how="left")
# join (distance)
df_tweets_geo = pd.merge(df_tweets_geo, df_distance, on=["id", "user_id"], how="left")

# Remove tweets where dialect is False
df_tweets_geo = df_tweets_geo.loc[df_tweets_geo["dialect"] != "False"]

df_tweets_geo_gender = pd.merge(df_tweets_geo, df_gender, on=["user_display_name"], how="left")

# Output
df_tweets_geo_gender.to_csv(args.output_tsv, index=False, sep="\t")
