import csv
import argparse
import requests
from bs4 import BeautifulSoup
import unicodedata

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
}


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


def get_nytimes_meta(url):
    # Extract text, twitter handle
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, "html.parser")
    twitter = [
        a["href"] for a in soup.find_all("a", href=True) if "twitter.com" in a["href"]
    ]
    twitter = twitter[0] if len(twitter) > 0 else None
    text = soup.find(id="byline").find("p").getText(separator=" ", strip=True)
    if text == "Advertisement":
        text = ""
    return {"twitter": twitter, "desc": text}


def get_washtimes_meta(url):
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, "html.parser")
    twitter = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if "twitter.com" in a["href"] and "/WashTimes" not in a["href"]
    ]
    twitter = twitter[0] if len(twitter) > 0 else None
    text = soup.find(class_="author-bio").getText(separator=" ", strip=True)
    return {"twitter": twitter, "desc": text}


def get_usatoday_meta(url):
    if url.startswith("/"):
        url = "https://www.usatoday.com" + url
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, "html.parser")
    twitter = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if "twitter.com" in a["href"] and "/usatoday" not in a["href"]
    ]
    twitter = twitter[0] if len(twitter) > 0 else None
    text = soup.find(class_="bio").getText(separator=" ", strip=True)
    return {"twitter": twitter, "desc": text}


def get_wsj_meta(url):
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, "html.parser")
    twitter = [
        a["href"]
        for a in soup.find(id="author-card").find_all("a", href=True)
        if "twitter.com" in a["href"]
    ]
    twitter = twitter[0] if len(twitter) > 0 else None
    if twitter and twitter.startswith("//"):
        twitter = twitter.replace("//", "https://")
    text = soup.find(id="author-card").getText(separator=" ", strip=True)
    return {"twitter": twitter, "desc": text}


def get_meta(record):
    hostname = record["hostname"]
    url = record["link"]
    r = {"twitter": None, "desc": ""}
    print(url)
    if "nytimes.com" in hostname:
        r = get_nytimes_meta(url)
    elif "usatoday.com" in hostname:
        r = get_usatoday_meta(url)
    elif "wsj.com" in hostname:
        r = get_wsj_meta(url)
    elif "washingtontimes.com" in hostname:
        r = get_washtimes_meta(url)
    else:
        pass

    r["desc"] = remove_control_characters(r["desc"].replace("\n", " "))

    record.update(r)
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist names and website information from an input TSV of news articles. Writes to <output_file>"
    )
    parser.add_argument("input_file", help="The input TSV to read")
    parser.add_argument("output_file", help="The output TSV to write")
    args = parser.parse_args()
    records = []

    with open(args.input_file) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        for row in reader:
            j = get_meta(row)
            records.append(j)

    with open(args.output_file, "w") as ofile:
        writer = csv.DictWriter(
            ofile,
            fieldnames=["name", "hostname", "link", "twitter", "desc"],
            delimiter="\t",
        )
        writer.writeheader()
        for record in records:
            writer.writerow(record)
