import argparse
import pandas as pd

from tqdm.auto import tqdm

parser = argparse.ArgumentParser(
    description='distance - compute distance between \"gij\" and predicate')
parser.add_argument('tweets_geo_tsv', type=str,
                    help='The TSV which contains all current tweets')
parser.add_argument('--output_html', type=str, default="distance_viz.html",
                    help='The HTML file to output to')


args = parser.parse_args()

df = pd.read_csv(args.tweets_geo_tsv, sep="\t")

df = df.loc[df["distance"] > 5]
df = df.sort_values(by=["distance"], ascending=False)

total_html = "<style>.subj { background-color: #FCE5F0; } .pred { background-color: #f0fce5; }</style>"

total_html = total_html + "<table>"

for index, row in tqdm(df.iterrows(), total=len(df), desc="Tweets processed"):
    if type(row["tokens"]) == float:
        continue

    row_html = "<tr><td>"

    row_html = row_html + str(row["id"]) + "</td><td>"
    
    for token_idx, token in enumerate(row["tokens"].split(" ")):
        token_html = token
        if token_idx == row["subject_index"]:
            token_html = f"<span class='subj'>{token}</span>"
        elif token_idx == row["predicate_index"]:
            token_html = f"<span class='pred'>{token}</span>"

        row_html = row_html + token_html + " "
    row_html = row_html + "</td></tr>"

    total_html = f"{total_html}\n{row_html}"

total_html = total_html + "</table>"

with open(args.output_html, "wt") as writer:
    writer.write(total_html)