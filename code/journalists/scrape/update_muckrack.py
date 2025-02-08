from squidtools import muckrack, robust_task, names

import argparse
import csv
import json
import random
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist names and website information from an input CSV of news articles. Writes to <output_file>"
    )
    parser.add_argument("json", help="The input JSON to read")
    parser.add_argument("tsv", help="The input JSON to read")
    args = parser.parse_args()
    scraper = muckrack.MuckrackScraper(
        os.getenv("MR_USERNAME"), os.getenv("MR_PW"), delay=8
    )
    records = []
    muckrack = json.load(open(args.json))
    with open(args.tsv) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        for row in reader:
            auth = row['author']
            muckrack[auth]['newspaper'] = row['sources']

    def handle(mr):
        if mr.get('url') and 'error' not in mr and mr.get('newspaper'):
            match_score = names.simpleMatchScore(mr.get('_pkey'), mr.get('name'))
            if match_score > 0.7:
                ret = scraper.scrape(
                    name=mr['_pkey'],
                    outlet=mr['newspaper'],
                    url=mr.get('url')
                )
                return ret
            else:
                return {
                    'error': 'MuckrackProfileNotFound',
                    'url': mr.get('url')
                }
        else:
            return mr

    results = robust_task.robust_task(
        muckrack, handle, progress_name="data/muckrack.update.progress.json"
    )
    print(json.dumps(results, indent=4))

       
