from squidtools import linkedin, robust_task, names

import argparse
import csv
import json
import sys
import os, requests
from squidtools.util import print_err

PX_API_KEY = os.getenv('PROXYCURL_API_KEY')

def proxycurl_url(url):

    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    api_key = 'l66A0AYEfQiDMhu3MBjzhA'
    header_dic = {'Authorization': 'Bearer ' + api_key}
    params = {
        'url': url,
        'fallback_to_cache': 'on-error',
        'use_cache': 'if-present',
        'extra': 'include',
    }
    response = requests.get(api_endpoint, params=params, headers=header_dic)
    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist Linkedin information from an input CSV of authors. Writes to STDOUT"
    )
    parser.add_argument("authors", help="The input tsv to read")
    args = parser.parse_args()

    journos = {}
    with open(args.authors) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        for row in reader:
            url = row['linkedin_url']
            name = row['clean_name']
            journos[name] = row

    def handle_journalist(j):
        # We use DDG search
        return proxycurl_url(j['linkedin_url'])

    results = robust_task.robust_task(
        journos,
        handle_journalist,
        progress_name='data/proxycurl.supp.progress.json'
    )
    print(json.dumps(results, indent=4))
