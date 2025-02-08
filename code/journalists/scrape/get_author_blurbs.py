"""
given an author name and potential newspaper employer, 
find their staff page, if any
"""
from squidtools import webscraper, robust_task, names
from squidtools.util import print_err
from selenium.webdriver.common.by import By
import argparse
import csv
import json
import sys
import os, requests

# this is deprecated 
def search_nyt(scraper, name):
    search_string_escaped = name.replace(" ", "%20")
    search_url_qw = f"http://qwant.com/?q=site:nytimes.com/by%20{search_string_escaped}" 
    scraper.nav(search_url_qw)
    links = scraper.find_elements('//a[@data-testid="serTitle"]')
    
    url = None
    for li in links:
        if 'nytimes.com/by' not in  li.get_attribute('href'):
            continue
        url = li.get_attribute('href')
        break
    scraper.nav(url)
    name = scraper.findElementText('//h1')
    byline = scraper.findElementText('//h2')
    text = scraper.findElements('//section[@id="byline"]/section/p')
    contacts = scraper.findElements('//div[@id="contact"]//a')
    contacts = [c.get_attribute('href') for c in contacts]
    linkedin = [c for c in contacts if 'linkedin' in c]
    return {
         'name': name,
         'byline': byline,
         'text': text,
         'url': url,
         'contacts': contacts,
         'linkedin': linkedin[0] if len(linkedin) else None
    }

def get_domain(source):
    sources = source.lower()

    if 'new york times' in sources or 'nyt' in sources:
        domain = 'nytimes.com'
    elif 'washington post' in sources or 'wapo' in sources:
        domain = 'washingtonpost.com'
    elif 'los angeles' in sources  or 'la times' in sources:
        domain = 'latimes.com'
    elif 'chicago' in sources:
        domain = 'chicagotribune.com'
    elif 'wsj' in sources or 'wall street journal' in sources:
        domain = 'wsj.com'
    elif 'latimes' in sources or 'los angeles' in sources:
        domain = 'latimes.com'
    elif 'usa today' in sources:
        domain = 'usatoday.com'
    else:
        print_err(f'unrecognized source {source}')
        raise Exception(sources)
    return domain

def search_is_a(name, source):
    search_string_escaped = f"{name} is a".replace(" ", "%20")
    domain = get_domain(source)
    search_url_qw = f"http://qwant.com/?q=site:{domain}%20{search_string_escaped}" 
    scraper.nav(search_url_qw)
    links = scraper.find_elements('//div[@data-testid="webResult"]')
    url = None
    for li in links:
        if domain not in li.get_attribute('domain'):
            continue
        try:
            text = li.find_element(By.XPATH, './/div[mark]')
            url = li.find_element(By.XPATH, './/a')
        except Exception:
            continue
        if text:
            text = text.text
            print(text)
            if text.startswith('By'):
                continue
            return {
                'url': url.get_attribute('href') if url else None,
                'text': text,
                'ents': names.get_ents(text)
            }
    return {
        'error': 'NoSummaryFound'
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist names and website information from an input CSV of news articles. Writes to <output_file>"
    )
    parser.add_argument("authors", help="The input json to read")
    args = parser.parse_args()

    journalists = {}
    with open(args.authors) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        for row in reader:
            name = row['clean_name']
            sources = row['og_sources'].split(',')[0]

            journalists[name] = {
                'name': name,
                'sources': sources,
            }


    scraper = webscraper.WebScraper()

    def handle_journalist(journo):
        obj = search_is_a(journo['name'], journo['sources'])
        return obj

    results = robust_task.robust_task(
        journalists,
        handle_journalist,
        progress_name='blurbs.progress.json'
    )
    print(json.dumps(results, indent=4))
