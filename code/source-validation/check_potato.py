"""
Python script to take annotations created by Potato workers 
and see if they correctly answered the testing questions.
"""

INPUT_DIR = 'annotation_output.250'
OUTFILE = f"{INPUT_DIR}.test_questions.tsv"

import argparse
import os
import json
from squidtools import util
import re

def process_directory(root_dir):
    result_array = []
    n_new_sources = 0

    for subdir, dirs, files in os.walk(root_dir):
        # Check if "annotated_instances.jsonl" exists in the current subdirectory
        if "annotated_instances.jsonl" in files:
            file_path = os.path.join(subdir, "annotated_instances.jsonl")
            coder_id = os.path.basename(subdir)
            if coder_id == 'test':
                continue
            
            with open(file_path, 'r') as file:
                for line in file:
                    # Parse each JSON object and add the subdirectory name as a field
                    json_object = json.loads(line.strip())
                    new_source_1 = json_object['label_annotations'].get('new_source_1')
                    new_source_2 = json_object['label_annotations'].get('new_source_2')

                    if ('testing' not in json_object['id']):
                        if new_source_1 is not None:
                            #print(new_source_1)
                            n_new_sources += 1
                        if new_source_2 is not None:
                            #print(new_source_2)
                            n_new_sources += 1
                        continue

                    """
                    "label_annotations": {
                        "existing_source_1": {"Person Name": "Anonymous", "Person Title": "N/A", "Organization": "N/A", "Document": "N/A", "Category": "other", "": "Yes"}, 
                        "existing_source_2": {"Person Name": "Jonathan H. Adler", "Person Title": "Law Professor", "Organization": "Case Western Reserve University", "Document": "N/A", "Category": "academic", "": "Yes"}, 
                        "existing_source_3": {"Person Name": "Anonymous", "Person Title": "Spokesman/Two people close to administration", "Organization": "The White House", "Document": "N/A", "Category": "bureaucrat", "": "Yes"},
                        "existing_source_4": {"Person Name": "Mitch Jones", "Person Title": "Policy Director", "Organization": "Food and Water Watch", "Document": "N/A", "Category": "nonprofit/activist", "": "Yes"}, 
                        "existing_source_5": {"Person Name": "Alice Hill", "Person Title": "Former Climate Planner", "Organization": "National Security Council during the Obama administration", "Document": "N/A", "Category": "bureaucrat", "": "Yes"}, 
                        "existing_source_6": {"Person Name": "Sherri Goodman", "Person Title": "Former Deputy Under Secretary of Defense for Environmental Security and Senior Fellow", "Organization": "Wilson Center\u2019s Environmental Change and Security Program", "Document": "N/A", "Category": "nonacademic expert/research", "": "Yes"}, 
                        "existing_source_7": {"Person Name": "Christopher Flavelle", "Person Title": "Spokesperson", "Organization": "American Petroleum Institute", "Document": "N/A", "": "no"}, 
                        "new_source_1": {"Person Name": "Tim Profeta", "Person Title": "Director", "Organization": "Nicholas Institute for Environmental Policy Solutions (Duke University)", "Document": "N/A", "Category": "academic"}
                    }, 
                    "span_annotations": {}, 
                    "behavioral_data": {"time_string": "Time spent: 0d 0h 18m 41s "}}
                    """

                    time = json_object['behavioral_data']['time_string']
                    checks = {}
                    checks['new_source_name'] = None
                    checks['new_source_category'] = None
                    if (new_source_1):
                        checks['new_source_name'] = new_source_1['Person Name'] == "Tim Profeta" or new_source_1['Person Name']
                        checks['new_source_category'] = new_source_1.get('Category') == "academic" or new_source_1.get('Category')
                    flavelle = json_object['label_annotations'].get('existing_source_7')
                    try:
                        checks['flavelle_no']  = flavelle and flavelle.get("") == 'no'
                    except:
                        import pdb;
                        pdb.set_trace()
                    alice = json_object['label_annotations'].get('existing_source_5')
                    checks['alice_corrected'] = alice and alice["Person Name"] == "Alice Hill"
                    checks['alice_yes'] = alice and alice.get('') == "Yes"
                    adler = json_object['label_annotations'].get('existing_source_2')
                    checks['adler_category'] = adler and adler['Category'] == "academic"
                    checks['adler_yes'] = adler and adler.get('') == "Yes"
                    checks['mitch_yes'] = json_object['label_annotations'].get('existing_source_4', {}).get('') == "Yes"
                    n_checks_passed = sum([int(c == True) for c in checks.values()])
                    res = {
                        'coder_id': os.path.basename(subdir),
                        'score': n_checks_passed / len(checks),
                        'n_checks_passed': n_checks_passed,
                        'time': time,
                    }
                    print(f"{res['coder_id']}: {res['score']}, {time}")
                    result_array.append(res)
    print(f"{n_new_sources} new sources")

    return result_array

def main():
    records = process_directory(INPUT_DIR)
    util.write_csv(records, OUTFILE, delimiter='\t')



if __name__ == "__main__":
    main()
