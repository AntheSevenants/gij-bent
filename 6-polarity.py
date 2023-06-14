import argparse
import pandas as pd

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm.auto import tqdm
from math import ceil

parser = argparse.ArgumentParser(
    description='polarity - detect sentiment for each tweet')
parser.add_argument('working_tsv', type=str,
                    help='The TSV which contains all current tweets')
parser.add_argument('--output_tsv', type=str, default="polarity.tsv",
                    help='The TSV to output the polarity information to')

args = parser.parse_args()

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

tokenizer = AutoTokenizer.from_pretrained("DTAI-KULeuven/robbert-v2-dutch-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("DTAI-KULeuven/robbert-v2-dutch-sentiment")

df = pd.read_csv(args.working_tsv, sep="\t")

#df = df.head(1000)

CHUNK_SIZE = 25

tweets = df["content"].tolist()
chunks = divide_chunks(tweets, CHUNK_SIZE)
total_chunks = ceil(len(tweets) / CHUNK_SIZE)

output_logits = []

for chunk in tqdm(chunks, total=total_chunks):
    inputs = tokenizer(chunk, return_tensors='pt', padding=True)
    output = model(**inputs)
    # Convert to regular floats
    output = output.logits.softmax(dim=-1).detach().tolist()

    output_logits += output

negative = list(map(lambda polarity: polarity[0], output_logits))
positive = list(map(lambda polarity: polarity[1], output_logits))

polarity_df = pd.DataFrame({"id": df["id"],
                          "negative": negative,
                          "positive": positive})

polarity_df.to_csv(args.output_tsv, index=False, sep="\t")