"""
Python script to take annotations created by Potato workers 
and create a TSV with the contained data
"""

INPUT_DIR = 'annotation_output.250'
ORIGINAL_SOURCES = '../../data/climate-excerpts/sources.gpt.250.json'
TEST_TSV = 'annotation_output.250.test_questions.tsv'
OUTFILE = f"{INPUT_DIR}.tsv"

import os
import csv
import json
from squidtools import util

def fetch_og_sources():
    records = {}
    with open(ORIGINAL_SOURCES, 'rt') as file:
        for line in file:
            article = json.loads(line)
            filename = article['filename']
            records[filename] = article
    return records

def fetch_good_ids():
    reader = csv.DictReader(open(TEST_TSV, 'rt'), delimiter='\t')
    ids = []
    for row in reader:
        if float(row['score']) >= 0.8:
            ids.append(row['coder_id'])
    return set(ids)

def get_n_new(obj):
    ns1 = obj['label_annotations'].get('new_source_1')
    ns2 = obj['label_annotations'].get('new_source_2')
    n = 0
    for ns in [ns1, ns2]:
        if ns is None: 
            continue
        if len(ns.keys()) < 2:
            continue
        n += 1
    return n

def get_existing(obj):
    srcs = []
    for i in range(1,15):
        keystr = f"existing_source_{i}"
        es = obj['label_annotations'].get(keystr)
        if es is None:
            break
        es['cite'] = es.get('')
        srcs.append(es)
    return srcs

def compare_categories(anno_es, og_sources):
    # Annotator existing sources should be in the same order as og_sources
    matches = 0
    corrections = 0
    unsure = 0

    for an, og in zip(anno_es, og_sources):
        an_cat = an.get('Category')
        if (an_cat == None):
            # Annotator did not provide a category, means no correction was made
            matches += 1
            continue
        an_cat = an_cat.lower()
        og_cat = og['category'].lower()
        name_match = og['person_name'] == an['Person Name']
        cat_match = an_cat == og_cat
        if (name_match and cat_match):
            # Confidently say the category matches
            matches += 1
        if (name_match and not cat_match):
            # Confidently say the category does not match
            corrections += 1
        if (not name_match):
            unsure += 1
    return {
        'matches': matches,
        'corrections': corrections,
        'unsure': unsure
    }





def process_directory(root_dir):
    valid_ids = fetch_good_ids()
    og_sources = fetch_og_sources()
    result_array = []

    for subdir, dirs, files in os.walk(root_dir):
        if "annotated_instances.jsonl" in files:
            file_path = os.path.join(subdir, "annotated_instances.jsonl")
            coder_id = os.path.basename(subdir)
            if coder_id not in valid_ids:
                continue
            
            # Read and process the contents of the file
            with open(file_path, 'r') as file:
                for line in file:
                    json_object = json.loads(line.strip())
                    if ('testing' in json_object['id']):
                        continue
                    # What do we even want to evaluate?
                    # Number of new sources
                    # Number of confirmed sources
                    # Number of false sources
                    # Number of category changes - but need the original data to evaluate this
                    n_new = get_n_new(json_object)
                    es = get_existing(json_object)
                    category_matches = compare_categories(es, og_sources[json_object['id']]['sources'])
                    print([e['cite'] for e in es])
                    result = {
                        'article_id': json_object['id'],
                        'n_new': get_n_new(json_object),
                        'n_existing': len(es),
                        'n_confirmed': len([e for e in es if e['cite'] == 'Yes' or e['cite'] == 'Yes-Dup']),
                        'n_no': len([e for e in es if e['cite'] == 'no']),
                        'n_unsure': len([e for e in es if e['cite'] == 'unsure']),
                        'n_none': len([e for e in es if e['cite'] == None]),
                        'coder_id': coder_id,
                        'n_cat_matches': category_matches['matches'],
                        'n_cat_corrections': category_matches['corrections'],
                        'n_cat_unsure': category_matches['unsure']
                    }
                   
                    result_array.append(result)

    return result_array

def main():
    records = process_directory(INPUT_DIR)
    util.write_csv(records, OUTFILE, delimiter='\t')



if __name__ == "__main__":
    main()
