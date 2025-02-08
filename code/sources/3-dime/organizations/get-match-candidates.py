import rapidfuzz
from squidtools import util
from multiprocessing import Pool
import itertools
import csv
import time


# Sample data loading: assume datasets are lists of dicts (from csv.DictReader)
# For simplicity, we'll assume the relevant field is called 'text'
def load_data_from_csv(filepath):
    with open(filepath, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        return [row for row in reader]


# Load your datasets
dime_entries = load_data_from_csv("dime_contributor_pac_clean.tsv")  # 2M records
orgs = load_data_from_csv("orgs_cleaned.tsv")  # 10K records

dime_names = [rapidfuzz.utils.default_process(row["contributor_name"]) for row in dime_entries]

def get_match_candidates(org_batch):
    results = []
    time_elapsed = 0
    n = len(org_batch)
    for i, org in enumerate(org_batch):
        t0 = time.time()
        candidates = {}
        candidates_jw = rapidfuzz.process.extract(
            org["contributor_name"],
            choices=dime_names,
            scorer=rapidfuzz.distance.JaroWinkler.similarity,
            processor=None,
            limit=100,
        )
        for c in candidates_jw:
            candidates[c[2]] = {
                'name': c[0],
                'dime_id': c[2],
                'jw_sim': c[1],
                'wr_sim': rapidfuzz.fuzz.WRatio(c[0], org['contributor_name'])
            }
        results.extend(candidates.values())
        time_elapsed += time.time() - t0
        if (i % 10 == 0 and i != 0):
            remaining = len(orgs) - i
            pct = round(i / len(orgs) * 100)
            avg_time = time_elapsed / i
            print(f"{pct}% ({i}/{len(orgs)}) ({round(avg_time, 2)}s per match, {round(avg_time * remaining)}s remaining)", end='\r')
    return results

results = get_match_candidates(orgs)

util.write_tsv(results, 'match-candidates.tsv')
