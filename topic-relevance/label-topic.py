import os
import argparse
import json
from data_wrangler import gpt_utils, robust_task

IDENTIFY_PROMPT = """
Does the following news article excerpt contain discussion of
the science of climate change, global warming, or impacts of climate change or climate change related policy? 
Be concise. End your answer with either "yes" or "no".
"""

def label_lines(lines):
    message, cost = gpt_utils.basic_prompt(IDENTIFY_PROMPT, "\n".join(lines))
    label = None
    if 'yes' in message.lower() and 'no' not in message.lower():
        label = True
    elif 'no' in message.lower():
        label = False
    else:
        print("Both no and yes in the response?")
    return label, cost


def make_paragraphs(f):
    text = "\n".join([lines.strip() for lines in f])
    return text.split("\n\n")


def label_file(filename):
    with open(filename, "rt") as f:
        lines = make_paragraphs(f)
        label, cost = label_lines(lines[0:5])
        results = {"filename": filename, "label": label, "cost": cost}
        return results


def get_files_in_dir(dirname):
    for filename in os.listdir(dirname):
        if filename.endswith(".txt"):
            yield os.path.join(dirname, filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Use ChatGPT to label news articles."
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to the txt file(s). If directory, extracts for every .txt file in the directory",
    )

    args = parser.parse_args()
    if os.path.isdir(args.path):
        os.chdir(args.path)
        files = get_files_in_dir('txt/')
        results = robust_task.robust_task(files, label_file, progress_name='labeling-progress.json')
        print(robust_task.naive_dict_to_tsv(results))
    else:
        res = label_file(args.path)
        print(json.dumps(res, indent=4))
