import rapidfuzz
from squidtools import util
import csv
import time


# Sample data loading: assume datasets are lists of dicts (from csv.DictReader)
# For simplicity, we'll assume the relevant field is called 'text'
def load_data_from_csv(filepath):
    with open(filepath, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        return [row for row in reader]


# Load your datasets
dime_entries = load_data_from_csv("dime-politicians.tsv")  # 2M records
orgs = load_data_from_csv("politicians.tsv")  # 10K records

dime_names = [rapidfuzz.utils.default_process(row["person_name"]) for row in dime_entries]

results = []
time_elapsed = 0
n = len(orgs)
for i, org in enumerate(orgs):
    t0 = time.time()
    candidates_jw = rapidfuzz.process.extract(
        org["person_name"],
        choices=dime_names,
        processor=None,
        limit=20,
    )
    for c in candidates_jw:
        results.append({
            'dime_name': c[0],
            'person_name': org['person_name'],
            'Cand.ID': dime_entries[c[2]]['Cand.ID'],
            'rf_sim': c[1],
        })
    time_elapsed += time.time() - t0
    if (i % 10 == 0 and i != 0):
        remaining = len(orgs) - i
        pct = round(i / len(orgs) * 100)
        avg_time = time_elapsed / i
        print(f"{pct}% ({i}/{len(orgs)}) ({round(avg_time, 2)}s per match, {round(avg_time * remaining)}s remaining)", end='\r')

util.write_tsv(results, 'match-candidates.tsv')
