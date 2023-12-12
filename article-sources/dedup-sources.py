"""
input is JSON
"""

SOURCE_NAME = 'sources.progress.json'

import argparse
import os
import json

def make_key(source):
    return '|'.join([source.get('person_name'), source.get('person_title'), source.get('organization'), source.get('document')])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Use ChatGPT to extract the journalist's sources from a plaintext news article."
    )
    parser.add_argument(
        "outn",
        type=str,
        help="Path to the output file"
    )
    args = parser.parse_args()

    with open(args.outn, 'wt') as of:
        os.chdir(os.path.dirname(args.outn))
        with open(SOURCE_NAME, 'rt') as f:
            for line in f:
                article = json.loads(line)
                sources = article['sources']
                deduped = {}
                for s in sources:
                    key = make_key(s)
                    if key in deduped:
                        deduped[key]['comments'] += s['comments']
                        print(key)
                    else:
                        deduped[key] = s
                article['sources'] = list(deduped.values())
                n_deduped = len(sources) - len(deduped)
                if (n_deduped > 0):
                    print(f"Removed {n_deduped}")
                of.write(json.dumps(article))
                of.write('\n')
            





