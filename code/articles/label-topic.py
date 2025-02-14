import os
import argparse
import csv
from squidtools import gpt_utils_async, robust_task, util

IDENTIFY_PROMPT = """
Does the following news article excerpt contain discussion of
the science of climate change, global warming, impacts of climate change,
or climate change related policy? 
Be concise. End your answer with either "yes" or "no".
"""


async def label_lines(txt):
    message, cost = await gpt_utils_async.system_prompt(
        IDENTIFY_PROMPT, txt, model="gpt-3.5-turbo", temp=0
    )
    label = None
    if "yes" in message.lower() and "no" not in message.lower():
        label = True
    elif "no" in message.lower():
        label = False
    else:
        util.print_err("Both no and yes in the response?")
    return label, cost


def make_paragraphs(f):
    text = "\n".join([lines.strip() for lines in f])
    return text.split("\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Use ChatGPT to label news articles.")
    parser.add_argument(
        "path", type=str, help="Path to the file containing list of files to label"
    )

    args = parser.parse_args()
    reader = csv.DictReader(open(args.path), delimiter="\t")
    os.chdir(os.path.dirname(args.path))
    files = {row["filename"]: row["excerpt"] for row in reader}
    files = {f: files[f] for f in files if files[f] is not None}

    async def label(filename):
        lines = files[filename]
        label, cost = await label_lines(lines)
        results = {"filename": filename, "label": label, "cost": cost}
        return results

    results = robust_task.async_robust_task(
        list(files.keys()),
        label,
        progress_name="topic-label.progress.json",
    )

    util.write_tsv(results, "topic-labels.tsv")
