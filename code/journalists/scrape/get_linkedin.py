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

# This script uses the proxy curl API to scrape linkedin profile information
# from input MuckRack profile data
# For accounts that have MuckRack linkedin pages, the script directly
# fetches data about the account from ProxyCurl using the ProxyCurl profile lookup
# If there is no data from MuckRack, the script uses ProxyCurl's
# person lookup tool to try to find the data

# We use the homebrewed Li-Scraper tool to perform lookups of LinkedIn URLs
# in cases where the LinkedIn link from muckrack is not well-formed with the
# linkedin.com/in/IDENTIFIER format.

# We also use the homebrewed Li-Scraper tool to perform lookups of LinkedIn 
# data when the person does not appear to exist in the ProxyCurl database

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


def proxycurl_url(scraper, linkedin_url, method='linkedin'):
    if method == 'linkedin' and 'linkedin.com/in/' not in linkedin_url:
        scraper.nav(linkedin_url)
        if 'linkedin.com/in/' in scraper.driver.current_url:
            linkedin_url = scraper.driver.current_url
        else:
            print_err(f"{linkedin_url} not found - searching...")
            raise BadURLException

    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    api_key = PX_API_KEY
    header_dic = {'Authorization': 'Bearer ' + api_key}
    params = {
        'url': linkedin_url,
        'fallback_to_cache': 'on-error',
        'use_cache': 'if-present',
        'twitter_profile_id': 'include',
        'extra': 'include',
    }
    response = requests.get(api_endpoint, params=params, headers=header_dic)
    return response.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist names and website information from an input CSV of news articles. Writes to <output_file>"
    )
    parser.add_argument("muckrack", help="The input json to read")
    parser.add_argument("authors", help="The input json to read")
    args = parser.parse_args()

    # First merge the muckrack data with the original author data
    muckrack = json.load(open(args.muckrack, 'rt'))

    journalists = {}
    with open(args.authors) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        for row in reader:
                name = row['author']
                sources = row['sources']
                mr_info = muckrack[name]
                linkedin_url = mr_info.get(
                    'linkedin_link', 
                )
                twitter_link = mr_info.get(
                    'twitter_link', 
                )

                journalists[name] = {
                    'name': name,
                    'sources': sources,
                    'mr_li_url': linkedin_url,
                    'mr_tw_url': twitter_link
                }


    liscraper = linkedin.LinkedInScraper(LI_USERNAME, LI_PW, delay=5)

    def handle_journalist(journo):
        result = None
        try:
            if journo['mr_li_url']:
                result = proxycurl_url(liscraper, journo['mr_li_url'])
            elif journo['mr_tw_url']:
                result = proxycurl_url(liscraper, journo['mr_tw_url'], method='twitter')
        except BadNameException as e:
            pass
        except BadURLException as e:
            print_err(e)
            pass
        if result == None:
            url = linkedin.guess_linkedin_profile_ddg(liscraper, journo['name'], journo['sources'])
            if url:
                return proxycurl_url(liscraper, url)
        raise ProfileNotFoundException(journo['name'])

    results = robust_task.robust_task(
        journalists,
        handle_journalist,
        progress_name='data/proxycurl.naive.progress.json'
    )
    print(json.dumps(results, indent=4))
