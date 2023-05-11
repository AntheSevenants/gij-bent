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
            parts = [token]

        _ = _ + parts
    tokens = _

    predicate_index = None
    subject_indices = []
    for idx, token in enumerate(tokens):
        # how do people WRITE these characters
        token = re.sub(r"(\u00e9|\u00e8)", "e", token)
        token = re.sub(r"\u00ed", "i", token)

        # Remove non-alpha characters
        token = re.sub(r"[^a-zà-üÀ-Ü]", "", token, flags=re.IGNORECASE)
        if re.match(f".*({'|'.join(needles)}).*", token):
            predicate_index = idx

        if re.match(f".*(ge|gij|gy|\\wg\\w).*", token):
            subject_indices.append(idx)

    # If no predicate found at the end, value will remain None
    if predicate_index is None:
        continue

    # If no subject found at the end, value will remain None
    if len(subject_indices) == 0:
        continue
        not_found.append(tokens)

    context = None
    distance = None
    # We test for the possible contexts where gij zijt/gij bent can appear
    if predicate_index - 1 in subject_indices:
        context = "main"
        distance = 1
        subject_index = predicate_index - 1
    elif predicate_index + 1 in subject_indices:
        context = "inversion"
        distance = 1
        subject_index = predicate_index + 1
    else:
        context = "other"
        # We find the subject closest to the predicate
        distances = list(map(lambda x: predicate_index - x, subject_indices))
        distances = list(filter(lambda x: x > 0, distances))

        subject_index = None

        try:
            distance = min(distances)
            subject_index = predicate_index - distance
        except:
            not_found.append([subject_indices, predicate_index, row["content"]])

    new_rows.append({"id": row["id"],
                     "user_id": row["user_id"],
                     "context": context,
                     "distance": distance,
                     "subject_index": subject_index,
                     "predicate_index": predicate_index,
                     "tokens": " ".join(tokens)})

distance_df = pd.DataFrame(new_rows)
distance_df.to_csv(args.output_tsv, index=False, sep="\t")

with open("error.json", "wt") as writer:
    writer.write(json.dumps(not_found))
