"""
Python script to take annotations created by Potato workers 
and create a TSV with the contained data
"""

INPUT_DIR = 'prolific.pilot100.annotations'
OUTFILE = f"{INPUT_DIR}.tsv"

import os
import json
from squidtools import util

def process_directory(root_dir):
    result_array = []

    for subdir, dirs, files in os.walk(root_dir):
        # Check if "annotated_instances.jsonl" exists in the current subdirectory
        if "annotated_instances.jsonl" in files:
            file_path = os.path.join(subdir, "annotated_instances.jsonl")
            
            # Read and process the contents of the file
            with open(file_path, 'r') as file:
                for line in file:
                    # Parse each JSON object and add the subdirectory name as a field
                    json_object = json.loads(line.strip())
                    relevance_obj = json_object['label_annotations'].get('affirmative_action_relevance')
                    stance_obj = json_object['label_annotations'].get('affirmative_action_stance')
                    relevance_label, relevance_numeric, stance_label, stance_numeric = None, None, None, None
                    if relevance_obj:
                        relevance_label = list(relevance_obj.keys())[0]
                        relevance_numeric = list(relevance_obj.values())[0]
                    if stance_obj:
                        stance_label = list(stance_obj.keys())[0]
                        stance_numeric = list(stance_obj.values())[0]
                    labels = {
                        'id': json_object['id'],
                        'relevance_label': relevance_label,
                        'relevance_numeric': relevance_numeric,
                        'stance_label': stance_label,
                        'stance_numeric': stance_numeric,
                        'coder_id': os.path.basename(subdir)
                    }
                    result_array.append(labels)

    return result_array

def main():
    records = process_directory(INPUT_DIR)
    util.write_csv(records, OUTFILE, delimiter='\t')



if __name__ == "__main__":
    main()
