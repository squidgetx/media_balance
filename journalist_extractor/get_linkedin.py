from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


import csv
from bs4 import BeautifulSoup
import argparse
import time
import json

from urllib.parse import urljoin, urlparse

driver = None


def auth():
    AUTH_URL = "https://www.linkedin.com/"
    driver.get(AUTH_URL)
    # manual log in
    input("Press enter once login is complete...")


def guess_linkedin_profile(name, newspaper, desc):
    search_string = f"{name} {newspaper}"
    search_string_escaped = search_string.replace(" ", "%20")
    search_url = f"https://www.linkedin.com/search/results/all/?keywords={search_string_escaped}&origin=GLOBAL_SEARCH_HEADER&sid=w7v"
    driver.get(search_url)
    time.sleep(2.5)

    url = None
    # First try to see if there is an exact name match
    result_nodes = driver.find_elements(
        By.XPATH, f"//div[contains(@class,'entity-result')]//a"
    )
    name_nodes = [n for n in result_nodes if name in n.get_attribute("innerText")]
    if len(name_nodes) > 0:
        url = name_nodes[0].get_attribute("href")
    else:
        print("  Exact match failed, falling back")

        # If there's no exact name match, (possibly because of middle names and such)
        # just grab the first link in the first child of the search results
        # as long as it's not "Posts"

        results = driver.find_elements(
            By.XPATH, "//div[@class='search-results-container']/div[1]"
        )
        if len(results) < 0 or "Posts" in results[0].text:
            # No results found if the first node is suggested posts, move on
            print("  No results found")
            return None

        links = results[0].find_elements(
            By.XPATH, "//div[contains(@class,'entity-result')]//a"
        )
        name_pieces = [n for n in name.split(" ") if len(n) > 1]
        name_nodes = [
            n
            for n in links
            if any([x in n.get_attribute("innerText") for x in name_pieces])
        ]
        if len(name_nodes) > 0:
            url = name_nodes[0].get_attribute("href")
        else:
            return None

    return urljoin(url, urlparse(url).path)


def scrape_linkedin_details(detail_url):
    driver.get(detail_url)
    time.sleep(1)
    expand_about = driver.find_elements(By.CLASS_NAME, "inline-show-more-text__button")
    for ele in expand_about:
        if "see more" in ele.text:
            ele.click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    div = soup.find(id="main")
    details = []
    if div and "Nothing to see" not in div.text:
        ul = div.find("ul")
        detail_lis = ul.findChildren("li", recursive=False)
        for li in detail_lis:
            info = li.find(class_="flex-row").find_all("span", {"aria-hidden": True})
            details.append([i.getText(strip=True) for i in info])
    return details


def scrape_linkedin_profile(url):
    driver.get(url)
    time.sleep(1)
    expand_about = driver.find_elements(By.CLASS_NAME, "inline-show-more-text__button")
    for ele in expand_about:
        if "see more" in ele.text:
            ele.click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    li_name = soup.find("h1").getText() if soup.find("h1") else None
    pronoun_span = main.find("span", class_="text-body-small")
    pronouns = None
    if pronoun_span:
        pronouns = pronoun_span.getText(separator=" ", strip=True)

    about = soup.find(id="about")
    if about:
        about = about.parent.getText(separator=" ", strip=True)

    educations = scrape_linkedin_details(url + "/details/education")
    experiences = scrape_linkedin_details(url + "/details/experience")

    return {
        "li_name": li_name,
        "url": url,
        "pronouns": pronouns,
        "about": about,
        "experience": experiences,
        "education": educations,
    }


# profile = guess_linkedin_profile('Somini Sengupta', 'new york times', '')
# linkedin_profile = scrape_linkedin_profile(profile)


def hostname_to_newspaper(hostname):
    if "nytimes.com" in hostname:
        return "new york times"
    elif "usatoday.com" in hostname:
        return "usa today"
    elif "wsj.com" in hostname:
        return "wall street journal"
    elif "washingtontimes.com" in hostname:
        return "washington times"
    else:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract journalist names and website information from an input CSV of news articles. Writes to <output_file>"
    )
    parser.add_argument("input_file", help="The input CSV to read")
    parser.add_argument("output_file", help="The output JSON to write")
    args = parser.parse_args()
    records = []

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    auth()
    count = 0
    with open(args.input_file) as ifile:
        reader = csv.DictReader(ifile, delimiter="\t")
        for row in reader:
            newspaper = hostname_to_newspaper(row["hostname"])
            print(row["name"])
            url = guess_linkedin_profile(row["name"], newspaper, desc="")

            if url:
                profile = scrape_linkedin_profile(url)
                profile.update(row)
                records.append(profile)
                count += 1
            else:
                row["error"] = "Linkedin search failed"
                records.append(row)
    print(count)

    with open(args.output_file, "w") as ofile:
        ofile.write(json.dumps(records))
