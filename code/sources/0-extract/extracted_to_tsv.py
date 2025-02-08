"""
Very first stage of source cleaning. Move from JSON to TSV
"""
import csv
import pdb
import json
import os
import argparse
from squidtools import util


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="clean json output from gpt and transform to tsv")
    parser.add_argument("json", type=str, help="Path to the sources progress.json file.")
    args = parser.parse_args()

    output_tsv = args.json.replace('.json', '.tsv')

    js_sources = []
    with open(args.json, 'rt') as jf:
        js_sources = json.load(jf)
    

    gpt = []
    field_names = [
        'person_name',
        'person_title',
        'organization',
        'document',
        'category',
        'comments',
        'cost'
    ]

    total_cost = 0
    empty = []
    for id, sources in js_sources.items():
        total_cost += sources["cost"]
        ss = sources["sources"]
        # Sometimes gpt annoyingly puts the results in a single-keyed dict
        #if len(ss) == 1 and isinstance(ss, dict):
        #    ss = next(iter(ss.values()))
        filename = sources["filename"]
        if len(ss) == 0:
            empty.append(filename)
        for q in ss:
            if 'category' in q:
                record = {'filename': filename}
                for fn in field_names:
                    record[fn] = q.get(fn)
                gpt.append(record)
            else:
                util.print_err(filename)
                import pdb;
                pdb.set_trace()

    writer = csv.DictWriter(
        open(output_tsv, "wt"), fieldnames=gpt[0].keys(), delimiter="\t"
    )
    writer.writeheader()
    writer.writerows(gpt)
    print(f"{len(js_sources)} articles analyzed")
    print(f"{len(gpt)} sources written to {output_tsv}, cost {total_cost}")
    print(f"{len(empty)} articles found with no sources")
       
