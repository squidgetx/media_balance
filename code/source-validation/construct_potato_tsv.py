"""
Python script to take annotations created by Potato workers 
and create a TSV with the contained data
"""

INPUT_DIR = 'annotation_output.250'
ORIGINAL_SOURCES = 'sources.gpt.250.json'
TEST_TSV = 'annotation_output.250.test_questions.tsv'
OUTFILE = f"{INPUT_DIR}.v2.tsv"

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

def get_new(obj):
    ns1 = obj['label_annotations'].get('new_source_1')
    ns2 = obj['label_annotations'].get('new_source_2')
    ns = [n for n in [ns1, ns2] if n is not None]
    srcs = []
    for n in ns:
        src = {}
        src['person_name.anno'] = n.get('Person Name')
        src['person_title.anno'] = n.get('Person Title')
        src['organization.anno'] = n.get('Organization')
        src['category.anno'] = n.get('Category')
        src['document.anno'] = n.get('Document') 
        srcs.append(src)
    return srcs


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
        es['src_n'] = i
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

def supplement(anno_es, og_sources):
    sources = []
    for an, og in zip(anno_es, og_sources):
        src = {}
        src['person_name.gpt'] = og['person_name']
        src['person_title.gpt'] = og['person_title']
        src['organization.gpt'] = og['organization']
        src['document.gpt'] = og['document']
        src['category.gpt'] = og['category']
        src['comment.gpt'] = og['comments']
        src['person_name.anno'] = an.get('Person Name')
        src['person_title.anno'] = an.get('Person Title')
        src['organization.anno'] = an.get('Organization')
        src['document.anno'] = an.get('Document')
        src['category.anno'] = an.get('Category')
        src['cite.anno'] = an['cite']
        src['src_n'] = an['src_n']
        sources.append(src)
    return sources

def process_directory(root_dir):
    valid_ids = fetch_good_ids()
    og_sources = fetch_og_sources()
    result_array = []

    for subdir, dirs, files in os.walk(root_dir):
        if "annotated_instances.jsonl" in files:
            file_path = os.path.join(subdir, "annotated_instances.jsonl")
            coder_id = os.path.basename(subdir)
            coder_quality = coder_id in valid_ids
            
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
                    es = get_existing(json_object)
                    es = supplement(es, og_sources[json_object['id']]['sources'])
                    ns = get_new(json_object)
                    for e in es:
                        e['article_id'] = json_object['id']
                        e['coder_id'] = coder_id
                        e['coder_qual'] = coder_quality
                        e['source_type'] = 'existing'
                        result_array.append(e)
                    for e in ns:
                        e['article_id'] = json_object['id']
                        e['coder_id'] = coder_id
                        e['coder_qual'] = coder_quality
                        e['source_type'] = 'new'
                        result_array.append(e)


    return result_array

def main():
    records = process_directory(INPUT_DIR)
    util.write_csv(records, OUTFILE, delimiter='\t')



if __name__ == "__main__":
    main()
