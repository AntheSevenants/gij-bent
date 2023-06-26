import argparse
import pandas as pd

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm.auto import tqdm
from math import ceil

parser = argparse.ArgumentParser(
    description='emotion - detect emotion for each tweet')
parser.add_argument('working_tsv', type=str,
                    help='The TSV which contains all current tweets')
parser.add_argument('--output_tsv', type=str, default="emotion.tsv",
                    help='The TSV to output the polarity information to')

args = parser.parse_args()

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

tokenizer = AutoTokenizer.from_pretrained("EmotioNL")
model = AutoModelForSequenceClassification.from_pretrained("EmotioNL")

df = pd.read_csv(args.working_tsv, sep="\t")

#df = df.head(1000)

CHUNK_SIZE = 25

tweets = df["content"].tolist()
chunks = divide_chunks(tweets, CHUNK_SIZE)
total_chunks = ceil(len(tweets) / CHUNK_SIZE)

output_emotions = []

for chunk in tqdm(chunks, total=total_chunks):
    inputs = tokenizer(chunk, return_tensors='pt', padding=True)
    output = model(**inputs)
    # Convert to regular floats
    output = output.logits.softmax(dim=-1).detach().tolist()

    emotions = []

    for output_logits in output:
        max_value = max(output_logits)
        max_index = output_logits.index(max_value)

        emotion = ['neutral', 'anger', 'fear', 'joy', 'love', 'sadness'][max_index]

        emotions.append(emotion)
        
    output_emotions += emotions

emotion_df = pd.DataFrame({"id": df["id"],
                          "emotion": output_emotions})

emotion_df.to_csv(args.output_tsv, index=False, sep="\t")