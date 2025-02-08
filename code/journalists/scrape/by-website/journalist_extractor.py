#!/usr/bin/env python3
"""
Fetch journalist names and metadata from an input CSV of articles
Usage: ./journalist_extractor <inputfile> <outputfile> --key <input CSV key>
"""

import argparse
import csv
import requests
from bs4 import BeautifulSoup
import urllib.parse

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
}


def extract_journalist(url):
    hostname = urllib.parse.urlsplit(url).hostname
    assert hostname is not None
    r = [{"error": "journalist extraction failed"}]
    try:
        if "nytimes.com" in hostname:
            r = extract_nyt(url)
        elif "usatoday.com" in hostname:
            r = extract_usatoday(url)
        elif "wsj.com" in hostname:
            r = extract_wsj(url)
        elif "washingtontimes.com" in hostname:
            r = extract_washtimes(url)
        else:
            r = [{"error": f"domain not supported: {hostname}"}]
    except Exception as e:
        print("Error when handling " + url)
        print(e)

    return {"url": url, "hostname": hostname, "authors": r}


def extract_nyt(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    bylines = soup.find_all(itemprop="name")

    return [
        {"name": node.text, "link": node.find("a")["href"] if node.find("a") else None}
        for node in bylines
    ]


def extract_wsj(url):
    def get_href(n):
        if not n:
            return None
        return n.get("href")

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    bylines = soup.find(class_="article-byline")
    data = [
        {"name": n.text, "link": get_href(n.find("a"))}
        for n in bylines.find_all("span")
    ]
    return data


def extract_usatoday(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    byline_container = soup.find(class_="gnt_ar_by") or soup.find(class_="gnt_ar_pb")
    links = byline_container.find_all("a")
    if links:
        return [{"name": n.text, "link": n["href"]} for n in links]
    else:
        return [{"name": byline_container.text, "link": None}]


def extract_washtimes(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    bylines = soup.find(class_="byline").find_all("a")
    data = [{"name": n.text, "link": n["href"]} for n in bylines]
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist names and website information from an input CSV/TSV of news articles. Writes to <output_file>"
    )
    parser.add_argument("input_file", help="The input TSV/CSV to read")
    parser.add_argument("output_file", help="The output TSV/CSV to write")
    parser.add_argument(
        "--key",
        dest="key",
        default="Article Link",
        help='The column name containing the article URLs. Default to "Article Link"',
    )
    args = parser.parse_args()
    records = []

    with open(args.input_file) as ifile:
        separator = "\t" if args.input_file.endswith(".tsv") else ","
        reader = csv.DictReader(ifile, delimiter=separator)
        for row in reader:
            if row.get("On Topic") == "No":
                continue
            j = extract_journalist(row[args.key])
            records.append(j)

    with open(args.output_file, "w") as ofile:
        writer = csv.DictWriter(
            ofile,
            fieldnames=["url", "hostname", "name", "link", "error"],
            delimiter="\t",
        )
        writer.writeheader()
        for record in records:
            for author in record["authors"]:
                error = author.get("error")
                if author.get("name") == "Associated Press":
                    error = "Associated Press"
                writer.writerow(
                    {
                        "url": record["url"],
                        "hostname": record["hostname"],
                        "name": author.get("name"),
                        "link": author.get("link"),
                        "error": error,
                    }
                )
