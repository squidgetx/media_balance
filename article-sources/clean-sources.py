import csv
import pdb
import json
import os
import argparse

# todo, move this somewhere else
def clean_ra_sources(tsv):
    reader = csv.DictReader(open(tsv), delimiter="\t")
    ra = {}
    for row in reader:
        filename = row["Article Name"] + ".txt"
        if filename not in ra:
            ra[filename] = []
        ra[filename].append(row)

    # now we have 2 dicts keyed by filename each containing an array of sources
    ra_clean = []
    for filename in ra:
        org_persons = [
            r["organizational affiliation"]
            for r in ra[filename]
            if r["name"] != "NA"
        ]
        for r in ra[filename]:
            if r["name"] == "NA" and r["organizational affiliation"] in org_persons:
                continue
            r["filename"] = filename
            r["organization"] = r["organizational affiliation"]
            del r["organizational affiliation"]
            ra_clean.append(r)
    writer = csv.DictWriter(
        open("ra_sources_clean.tsv", "wt"),
        fieldnames=ra_clean[0].keys(),
        delimiter="\t",
    )
    writer.writeheader()
    writer.writerows(ra_clean)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="clean json output from gpt")
    parser.add_argument("json", type=str, help="Path to the sources progress.json file.")
    args = parser.parse_args()

    js_sources = []
    with open(args.json, 'rt') as jf:
        js_sources = [json.loads(line) for line in jf]

    gpt = []

    total_cost = 0
    for sources in js_sources:
        total_cost += sources["cost"]
        ss = sources["sources"]
        # this is mad annoying LOL
        if "sources" in ss:
            ss = ss["sources"]
        if "quotations" in ss:
            ss = ss["quotations"]
        elif "people" in ss:
            ss = ss["people"]
        elif "people_quoted" in ss:
            ss = ss["people_quoted"]

        if "organizations" in ss:
            ss.extend(ss["organizations"])
        filename = os.path.basename(sources["filename"])
        print(filename)
        for q in ss:
            if q["name"]:
                q["filename"] = filename
                if "organizational affiliation" in q:
                    q["organizational_affiliation"] = q["organizational affiliation"]
                    del q["organizational affiliation"]

                gpt.append(q)

    os.chdir(os.path.dirname(args.json))
    writer = csv.DictWriter(
        open("gpt_sources_clean.tsv", "wt"), fieldnames=gpt[0].keys(), delimiter="\t"
    )
    writer.writeheader()
    writer.writerows(gpt)
    print(f"{len(js_sources)} articles extracted, cost {total_cost}")
       
