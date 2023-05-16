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
parser.add_argument('--skip_list', type=str, default="",
                    help='The list of manually scrapped tweets')
parser.add_argument('--output_tsv', type=str, default="distance.tsv",
                    help='The TSV to output the distance information to')

args = parser.parse_args()

df = pd.read_csv(args.working_tsv, sep="\t")

new_rows = []

skip_list = []
if args.skip_list != "":
    with open(args.skip_list, "rt") as reader:
        skip_list = json.loads(reader.read())

print("Downloading Dutch tokeniser")
nltk.download('punkt')

not_found = []

for index, row in tqdm(df.iterrows(), total=len(df), desc="Tweets processed"):
    if row["id"] in skip_list:
        continue

    tweet = row["content"]

    # Apply some substitutions
    tweet = re.sub(r"\bof maakt het juridisch geen verschil of aan\b", "of maakt het juridisch geen verschil of ge aan", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"\bhe zijt\b", "ge zijt", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"\bals gelaten\b", "als ge later", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"\bdjeezes\\ud83e\\udd2agij\b", "djeezes \ud83e \udd2a gij", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"\bdij zijt\b", "gij gij", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"\bals he een\b", "als ge een", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"\bwie zijt hij\b", "wie zijt gij", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"\bdjeezes\ud83e\udd2agij\b", "bdjeezes \ud83e \udd2a gij", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"([!.,;?])+", r"\1", tweet, flags=re.IGNORECASE)
    tweet = re.sub(r"\b\+\b", " + ", tweet, flags=re.IGNORECASE)

    # Tokenise
    tokens = nltk.word_tokenize(tweet.lower(), language='dutch')

    if (row["construction_type"] == "bent"):
        needles = ["bent", "bende"]
    elif (row["construction_type"] == "zijt"):
        needles = ["zijt", "zyt", "zijde", "zyde", "zedde"]

    _ = []
    # Correct boomer spelling
    for token in tokens:
        if len(token) >= 2:
            parts = token.split(".")

            if re.match(f"\\balsge\\b", token,flags=re.IGNORECASE):
                parts = [ "als", "ge" ]
            elif re.match(f"\\bd?age\\b", token,flags=re.IGNORECASE):
                parts = [ "da", "ge" ]
            elif re.match(f"\\bdaje?\\b", token,flags=re.IGNORECASE):
                parts = [ "da", "je" ]
            elif re.match(f"\\bal?s?je\\b", token,flags=re.IGNORECASE):
                parts = [ "as", "je" ]
            elif re.match(f"\\bomdage\\b", token,flags=re.IGNORECASE):
                parts = [ "omda", "ge" ]
            elif re.match(f"\\bofdage\\b", token,flags=re.IGNORECASE):
                parts = [ "of", "da", "ge" ]
            elif re.match(f"\\bdagij\\b", token,flags=re.IGNORECASE):
                parts = [ "da", "gij" ]
            elif re.match(f"\\balsde\\b", token,flags=re.IGNORECASE):
                parts = [ "als", "ge" ]
            elif re.match(f"\\bgijzelf\\b", token,flags=re.IGNORECASE):
                parts = [ "gij", "zelf" ]
            elif re.match(f"\\bdad+e\\b", token,flags=re.IGNORECASE):
                parts = [ "dat", "ge" ]
            elif re.match(f"\\bwadagy\\b", token,flags=re.IGNORECASE):
                parts = [ "wa", "da", "gy" ]
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
        if re.match(f"^({'|'.join(needles)})$", token):
            if predicate_index is None:
                predicate_index = idx

        if re.match(f"\\b(ge|gi*j*|gy|g|gie|gelle|gin|gulder|u|ji+j*|je)\\b", token, flags=re.IGNORECASE):
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
    # TODO: "en blijft" in inversion "bent en blijft gij"
    # TODO: "zijt alleen gij" in inversion
    elif predicate_index + 1 in subject_indices:
        context = "inversion"
        distance = 1
        subject_index = predicate_index + 1
    elif " ".join(tokens[predicate_index:predicate_index+4]) == "bent en blijft gij":
        context = "inversion"
        distance = 3
        subject_index = predicate_index + 3
    elif " ".join(tokens[predicate_index:predicate_index+3]) == "zijt alleen gij":
        context = "inversion"
        distance = 2
        subject_index = predicate_index + 2
    # Order of if statement guarantees no fronted inversion is possible
    elif predicate_index == 0:
        subject_index = None
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

    # Reset contexts with wrong subjects
    if subject_index is not None:
        subject_form = tokens[subject_index]
        if not re.match(f"\\b(ge|gi+j*|gy|g|gie|gelle|gin|gulder)\\b", subject_form, flags=re.IGNORECASE):
            subject_index = None
            context = None
            distance = None

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
