import argparse
import pandas as pd
from tqdm.auto import tqdm
from gender_from_name.detector import get_gender

parser = argparse.ArgumentParser(
    description='gender-detect - detect gender for each account')
parser.add_argument('working_tsv', type=str,
                    help='The TSV which contains all current tweets')
parser.add_argument('--output_tsv', type=str, default="gender.tsv",
                    help='The TSV to output the gender information to')

args = parser.parse_args()

df = pd.read_csv(args.working_tsv, sep="\t")

new_rows = []

display_names = df["user_display_name"].unique().tolist()

for display_name in tqdm(display_names, desc="Accounts processed"):
    gender = get_gender(display_name)

    new_rows.append({"display_name": display_name,
                     "gender": gender})


gender_df = pd.DataFrame(new_rows)
gender_df.to_csv(args.output_tsv, index=False, sep="\t")