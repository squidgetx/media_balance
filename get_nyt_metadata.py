"""
Script to pull nyt article metadata
Requires NYT_KEY and NYT_SECRET env variables set
"""

from dateutil import parser, rrule
import requests
import os
import argparse
import pandas

DATA_DIR = "nyt-metadata"
OVERWRITE = True


def clean_record(record):
    del record["multimedia"]
    record["keywords"] = ",".join([k["value"] for k in record["keywords"]])
    record["headline"] = record["headline"].get("main")
    record["authors"] = ",".join(
        [a["firstname"] + " " + a["lastname"] for a in record["byline"]["person"]]
    )
    record["byline"] = record["byline"]["original"]
    return record


def get(dt):
    filepath = f"{DATA_DIR}/{dt.year}-{dt.month}.tsv"
    print(f"Fetching data for {dt.year}-{dt.month}")
    if os.path.exists(filepath) and not OVERWRITE:
        print(f"  {filepath} already exists, skipping")
        return
    query = f"https://api.nytimes.com/svc/archive/v1/{dt.year}/{dt.month}.json?api-key={os.environ['NYT_KEY']}"
    result = requests.get(query).json()
    if "fault" in result:
        # TODO: if you get rate limited this fails, so could be nice to retry this
        print(result)
        return
    records = [
        clean_record(r)
        for r in result["response"]["docs"]
        if r["document_type"] == "article"
    ]
    df = pandas.DataFrame.from_records(records)
    df.to_csv(f"{DATA_DIR}/{dt.year}-{dt.month}.tsv", sep="\t")


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description="Fetch NYT metadata from NYT API. Stores output in JSON files in nyt-data directory"
    )
    arg_parser.add_argument(
        "-start",
        dest="start",
        required=True,
        help="ISO formatted start year/date for query (ex: 2020-01).",
    )
    arg_parser.add_argument(
        "-end",
        dest="end",
        required=True,
        help="ISO formatted end year/date for query (ex: 2021-01).",
    )

    args = arg_parser.parse_args()

    start = parser.parse(args.start)
    end = parser.parse(args.end)

    for dt in rrule.rrule(freq=rrule.MONTHLY, dtstart=start, until=end):
        get(dt)
