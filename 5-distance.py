import argparse
import pandas as pd
import nltk
import json
import re

from tqdm.auto import tqdm

parser = argparse.ArgumentParser(
    description='distance - compute distance between \"gij\" and predicate')
parser.add_argument('working_tsv', type=str,
                    help='The TSV which contains all current tweets')
parser.add_argument('--output_tsv', type=str, default="distance.tsv",
                    help='The TSV to output the distance information to')

args = parser.parse_args()

df = pd.read_csv(args.working_tsv, sep="\t")

new_rows = []

print("Downloading Dutch tokeniser")
nltk.download('punkt')

not_found = []

for index, row in tqdm(df.iterrows(), total=len(df), desc="Tweets processed"):
    # Tokenise
    tokens = nltk.word_tokenize(row["content"].lower(), language='dutch')

    if (row["construction_type"] == "bent"):
        needles = ["bent", "bende"]
    elif (row["construction_type"] == "zijt"):
        needles = ["zijt", "zyt", "zijde", "zyde", "zedde"]

    _ = []
    # Correct boomer spelling
    for token in tokens:
        if len(token) >= 2:
            parts = token.split(".")
        else:
            parts = [ token ]

        _ = _ + parts
    tokens = _

    predicate_index = None
    subject_index = None
    for idx, token in enumerate(tokens):
        # how do people WRITE these characters
        token = re.sub(r"\u00e9", "e", token)
        token = re.sub(r"\u00ed", "i", token)
        token = re.sub(r"\u00e8", "e", token)

        # Remove non-alpha characters
        token = re.sub(r"[^a-zà-üÀ-Ü]", "", token, flags=re.IGNORECASE)
        if re.match(f".*({'|'.join(needles)}).*", token):
            predicate_index = idx

        if re.match(f"(ge|gij|gy)", token):
            subject_index = idx

    # If no predicate found at the end, value will remain None
    if predicate_index is None:
        pass

    # If no subject found at the end, value will remain None
    if subject_index is None:
        not_found.append(tokens)

with open("error.json", "wt") as writer:
    writer.write(json.dumps(not_found))
