import argparse
import pandas as pd
import concurrent.futures

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


def process_name(display_name):
    gender = get_gender(display_name)
    return (display_name, gender)
    #return (display_name, "sjarel")

user_display_names = []
genders = []

# Start a processing pool
with concurrent.futures.ProcessPoolExecutor() as executor:
    # For each file, spawn a new process
    futures = [executor.submit(process_name, display_name) for display_name in display_names]
    
    # Register a tqdm progress bar
    progress_bar = tqdm(total=len(display_names), desc='Accounts processed')


    # Loop over future results as they become available
    for future in concurrent.futures.as_completed(futures):
        # Get result
        display_name, gender = future.result()

        progress_bar.update(n=1)  # Increments counter

        # Add the found results to the current results
        user_display_names.append(display_name)
        genders.append(gender)

# Create a data frame from the results
gender_df = pd.DataFrame({"user_display_name": user_display_names,
                          "gender": genders})
gender_df.to_csv(args.output_tsv, index=False, sep="\t")
