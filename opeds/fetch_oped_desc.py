"""
Fetch description of oped authors from NYT
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

import csv
import time
import pdb
import random
import pandas as pd

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def auth():
    AUTH_URL = 'https://myaccount.nytimes.com/auth/enter-email'
    driver.get(AUTH_URL)
    # manual log in 
    input("Press enter once login is complete...")


def get_author_desc(article_url, author_name, last_author_desc):
    if (author_name in last_author_desc):
        return last_author_desc
    driver.get(article_url)
    time.sleep(random.random() + 0.5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1 + random.random())
    # Create list of names to check. Start with the full name, then surname
    names = author_name.split(" ")
    names.append(author_name)
    names.reverse()
    rval = ''
    for name in names:
        try:
            eles = driver.find_elements(By.XPATH, f"""//p[contains(., "{name}")]""")
            if eles:
                rval = '|'.join([e.text for e in eles])
                break
        except:
            continue

    return rval
    
if __name__ == "__main__":
    #auth()

    # Read from FILE which contains a csv of author_names and web_urls
    # Output OUT csv which contains one row for each INDIVIDUAL author and any related text from NYT webpage
    FILE = 'oped_authors_2020.csv'
    OUT = "authors.csv"

    skip = []
    fieldnames = []
    with open(OUT) as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        skip = [row['author_name'] for row in reader if row['author_desc'] != '']

    i = 0
    with open(FILE) as csvfile:
        with open(OUT, 'a') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            reader = csv.DictReader(csvfile)
            for row in reader:
                authors = row['authors'].split(',')
                author_desc = ''
                for author in authors:
                    if author in skip:
                        print(f"Skipping {author}")
                        continue

                    author_desc = get_author_desc(
                        row['web_url'], 
                        author, 
                        last_author_desc=author_desc
                    )
                    record = {
                        "web_url": row['web_url'],
                        "author_desc": author_desc,
                        "author_name": author,
                        "co-authors": [a for a in authors if a != author]
                    }
                    writer.writerow(record)
                i += 1
                if (i % 10 == 0):
                    outfile.flush()
                print(i, end='\r')


