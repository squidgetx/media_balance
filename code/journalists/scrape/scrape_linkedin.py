from squidtools import linkedin, robust_task, names

import argparse
import csv
import json
import sys
import os, requests
from squidtools.util import print_err

PX_API_KEY = os.getenv('PROXYCURL_API_KEY')
LI_USERNAME=os.getenv('LI_USERNAME')
LI_PW=os.getenv('LI_PW')

class BadURLException(Exception):
    pass

class BadNameException(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
    pass

class ProfileNotFoundException(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
    pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("authors", help="The input TSV to read")
    args = parser.parse_args()

    # First merge the muckrack data with the original author data
    reader = csv.DictReader(open(args.authors), delimiter='\t')
    urls = {}
    for row in reader:
        linkedin_url = row.get(
            'linkedin_url', 
        )
        name = row['clean_name']
        if linkedin_url:
            urls[linkedin_url] = {
                'url': linkedin_url,
                'name': name, 
            }

    liscraper = linkedin.LinkedInScraper(LI_USERNAME, LI_PW, delay=10)

    def handle_journalist(name):
        j = urls[name]
        if j['url'] is not None:
            return liscraper.scrape(j['name'], desc='', url=j['url'])
        return None

    results = robust_task.robust_task(
        list(urls.keys()),
        handle_journalist,
        progress_name='data/simple.linkedin.scrape.json'
    )
    print(json.dumps(results, indent=4))
