import json
import pandas as pd

bent_df = pd.read_csv("corpus/corpus_bent.csv", sep="\t")
zijt_df = pd.read_csv("corpus/corpus_zijt.csv", sep="\t")

df = pd.concat([bent_df, zijt_df])

with open("keep_list.json", "rt") as reader:
    keep_list = json.loads(reader.read())
    df = df[df["tweet_id"].isin(keep_list)]

# Again, remove duplicates
df = df.drop_duplicates(subset=['tweet_id'])

df.to_csv("corpus_shared.tsv", sep="\t", index=False)