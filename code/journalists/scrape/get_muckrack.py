from squidtools import muckrack, robust_task

import argparse
import csv
import json
import random
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist names and website information from an input CSV of news articles. Writes to <output_file>"
    )
    parser.add_argument("input_file", help="The input CSV to read")
    args = parser.parse_args()
    scraper = muckrack.MuckrackScraper(
        os.getenv("MR_USERNAME"), os.getenv("MR_PW"), delay=8
    )
    records = []
    with open(args.input_file) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        journalists = {row["author"]: row["sources"] for row in reader}
        journo_list = list(journalists.keys())
        random.shuffle(journo_list)

        def handle_journalist(name):
            try:
                return scraper.scrape(name, journalists[name])
            except muckrack.MuckrackProfileNotFound:
                return {"error": "MuckRackProfileNotFound"}

        results = robust_task.robust_task(
            journo_list, handle_journalist, progress_name="data/muckrack.progress.json"
        )
        print(json.dumps(results, indent=4))
