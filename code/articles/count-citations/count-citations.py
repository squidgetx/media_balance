import os
import nltk
import argparse
import json
import csv
from colorist import Color
from squidtools import robust_task, util
import itertools

def count_cite_words(line):
    words = line.split(' ')
    in_quote = False
    n_cw = 0
    dbg = ""

    for word in words:
        if not in_quote and (word.startswith('"') or word.startswith('“')):
            in_quote = True
            dbg += Color.CYAN
        if in_quote == True:
            n_cw += 1
        dbg += word + ' '
        if in_quote and (word.endswith('"') or word.endswith('”')):
            in_quote = False
            dbg += Color.OFF
    if test_cite_line(line):
        dbg = Color.RED + dbg + Color.OFF
    #print(dbg)
    return n_cw


def count_words(line):
    return len(line.split(' '))

def test_cite_line(line):
    matches = ['"', '”', 'said', 'according', 'reported', 'say', 'reports', 'statement']
    for m in matches:
        if m in line.lower():
            return True
    return False


def count_cites(lines):
    results = {}
    cite_words = [count_cite_words(l) for l in lines]
    results['all_words'] = sum([count_words(l) for l in lines])
    results['n_cite_words'] = sum(cite_words)
    results['n_lines'] = len(lines)
    results['n_cite_lines'] = sum([test_cite_line(l) for l in lines])
    results['n_words_cite_lines'] = 0
    for l in lines:
        if test_cite_line(l):
            results['n_words_cite_lines'] += count_words(l)
    return results

def make_paragraphs(f):
    text = " ".join([lines.strip() for lines in f])
    sentes = nltk.sent_tokenize(text)
    return [s.strip() for s in sentes if len(s.strip()) > 0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Use ChatGPT to label news articles.")
    parser.add_argument(
        "path", type=str, help="Path to the file containing list of files to label"
    )

    args = parser.parse_args()
    reader = csv.DictReader(open(args.path), delimiter="\t")
    os.chdir(os.path.dirname(args.path))
    files = {row["filename"]: row["textfile"] for row in reader}
    files = {f:files[f] for f in files if files[f] is not None}

    def count_cites_task(filename):
        textname = files[filename]
        lines = make_paragraphs(open(textname, 'rt'))
        results = count_cites(lines)
        results['filename'] = filename
        return results
    
    records = []
    for file in files:
        rec = count_cites_task(file)
        records.append(rec)


    util.write_tsv(records, 'citation-counts.tsv')