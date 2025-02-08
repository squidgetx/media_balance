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
    api_key = PX_API_KEY
    header_dic = {'Authorization': 'Bearer ' + api_key}
    params = {
        'twitter_profile_url': url,
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

    # First merge the muckrack data with the original author data
    urls = set()
    with open(args.authors) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        for row in reader:
            url = row['mr_tw_url']
            if url != 'NA':
                urls.add(url)

    def handle_journalist(tw_url):
        # We use DDG search
        return proxycurl_url(tw_url)

    results = robust_task.robust_task(
        list(urls),
        handle_journalist,
        progress_name='data/proxycurl.twitter.progress.json'
    )
    print(json.dumps(results, indent=4))
