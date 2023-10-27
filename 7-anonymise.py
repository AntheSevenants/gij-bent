import argparse
import pandas as pd

parser = argparse.ArgumentParser(
    description='anonymise - anonymise the dataset for public sharing')
parser.add_argument('working_tsv', type=str,
                    help='The TSV which contains all tweets with identifiable information')
parser.add_argument('--output_tsv', type=str, default="tweets_geo.tsv",
                    help='The TSV to output the merged files to')

args = parser.parse_args()

# Read the dataframe
df_tweets = pd.read_csv(args.working_tsv, sep="\t")

# Define the columns to keep
kept_columns = ["construction_type", "year", "place_full_name",
                "lat", "long", "norm_lat",
                "norm_long", "dialect", "distance_from_antwerp", "context",
                "gender", "mentioned_users_count", "user_id", "username"]

# Select only the kept columns
df_anon = df_tweets[kept_columns]

# Now, anonymise the user IDs
df_anon = df_anon.assign(user_id=df_anon.user_id.factorize()[0],
                         username=df_anon.username.factorize()[0])

# Cast them as strings to not cause any type issues later down the line
df_anon["user_id"] = df_anon["user_id"].apply(lambda user_id: f"user_id_{str(user_id)}")
df_anon["username"] = df_anon["username"].apply(lambda username: f"username_{str(username)}")

# Output
df_anon.to_csv(args.output_tsv, index=False, sep="\t")