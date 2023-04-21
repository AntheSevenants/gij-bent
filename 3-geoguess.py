import argparse
import pandas as pd
import helpers.geolocator
from helpers.dialect_resolution_service import DialectResolutionService

from tqdm.auto import tqdm

parser = argparse.ArgumentParser(
    description='geoguess - provide latlong and dialect area information for each tweet')
parser.add_argument('working_tsv', type=str,
                    help='The TSV which contains all current tweets')
parser.add_argument('--output_tsv', type=str, default="geo.tsv",
                    help='The TSV to output the geo information to')

args = parser.parse_args()

df = pd.read_csv(args.working_tsv, sep="\t")

dialect_resolution = DialectResolutionService("dialects.json", "dialect")

new_rows = []

for index, row in tqdm(df.iterrows(), total=len(df), desc="Tweets processed"):
    lat, long = helpers.geolocator.geolocate(row["place_full_name"])
    dialect = dialect_resolution.point_to_dialect(lat, long)
    distance_from_antwerp = helpers.geolocator.distance_from_antwerp(lat, long)

    new_rows.append({"id": row["id"],
                     "lat": lat,
                     "long": long,
                     "dialect": dialect,
                     "distance_from_antwerp": distance_from_antwerp})


geo_df = pd.DataFrame(new_rows)
geo_df.to_csv(args.output_tsv, index=False, sep="\t")
