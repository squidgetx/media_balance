from squidtools import linkedin, robust_task, names

import argparse
import csv
import json
import sys
import os, requests
from squidtools.util import print_err

LI_USERNAME=os.getenv('LI_USERNAME')
LI_PW=os.getenv('LI_PW')

from get_linkedin import proxycurl_url, ProfileNotFoundException

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist Linkedin information from an input CSV of authors. Writes to STDOUT"
    )
    parser.add_argument("authors", help="The input tsv to read")
    args = parser.parse_args()

    # First merge the muckrack data with the original author data
    journalists = {}
    with open(args.authors) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        for row in reader:
                name = row['og_name']
                journalists[name] = row

    liscraper = linkedin.LinkedInScraper(LI_USERNAME, LI_PW, delay=5)    

    def handle_journalist(journo):
        # We use DDG search
        name = journo['clean_name']
     
        url = linkedin.guess_linkedin_profile_ddg(
                liscraper, 
                name,
                'writer'
        )
        # Don't scrape the profile if it's the same one that we already have. 
        if url is not None:
            if journo['linkedin_id'] in url:
                print_err(f"Already have {url} recorded")
                return {
                     'error': "Already have {url} recorded"
                }
            print_err(f"Proxycurling {url}")
            return proxycurl_url(liscraper, url)
        else:
            print_err("Couldn't find a valid linkedin profile")
            raise ProfileNotFoundException(name)

    results = robust_task.robust_task(
        journalists,
        handle_journalist,
        progress_name='data/proxycurl.redos.progress.json'
    )
    print(json.dumps(results, indent=4))
