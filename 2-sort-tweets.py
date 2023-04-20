import argparse
import json
import pandas as pd

from glob import glob
from pathlib import Path
from tqdm.auto import tqdm

parser = argparse.ArgumentParser(
    description='sort-tweets - convert tweets to TSV and keep only relevant ones')
parser.add_argument('corpus_directory', type=str, help='path to the directory with all retrieved tweets')
parser.add_argument('working-tsv', type=str, help='The TSV which contains all current tweets')

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

print(f"Found {len(good_tweets)} good tweets")