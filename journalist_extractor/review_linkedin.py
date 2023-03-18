import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
import time
import json

journalists = json.load(open("tmp/4.json"))
n_errors = sum([j.get("error") is not None for j in journalists])
n_journalists = len(journalists)
print(
    f"Scraped {n_journalists - n_errors} journalists from linkedin, {n_errors} failures"
)
for j in journalists:
    print(j["name"] + " " + j["hostname"])
    url = j.get("url", "")
    if url != "":
        url = urljoin(url, urlparse(url).path)
    print("  " + url)
