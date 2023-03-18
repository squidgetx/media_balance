"""
Code to guess a twitter handle given a name and 
some unstructured text about the person.
"""
import csv
import os
import pandas
import pdb
import requests
import string
import time

import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

SEARCH_URL = "https://api.twitter.com/1.1/users/search.json"
BEARER_TOKEN = os.environ["BEARER_TOKEN"]

STOPWORDS = stopwords.words("english")


def get_user_search_query(username, desc):
    query = f"{SEARCH_URL}?q={username}&count=5"
    return query


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v3TweetLookupPython"
    return r


def connect_to_endpoint(url, backoff=0):
    response = requests.request("GET", url, auth=bearer_oauth)
    if response.status_code == 429:
        delay = pow(2, backoff) * 5
        print(f"(429) hit rate limit... sleeping for {delay}")
        time.sleep(delay)
        return connect_to_endpoint(url, backoff + 1)
    if response.status_code != 200:
        print(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
        return None
    return response.json()


def clean_record(response):
    return {
        "id": f"{response['id']}",
        "description": response["description"],
        "followers_count": response["followers_count"],
        "verified": response["verified"],
        "location": response["location"],
        "name": response["name"],
        "username": response["screen_name"],
    }


stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), " ") for char in string.punctuation)


def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]


def normalize(text):
    """remove punctuation, lowercase, stem"""
    return [
        w
        for w in nltk.word_tokenize(text.lower().translate(remove_punctuation_map))
        if w not in STOPWORDS and w not in string.punctuation
    ]


def extract_features(user, name, desc):
    vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words="english")
    tfidf = vectorizer.fit_transform([user["description"], desc])
    sim = ((tfidf * tfidf.T).A)[0, 1]
    user["description_similarity"] = sim
    twitter_desc_tokens = set(normalize(user["description"]))
    desc_tokens = set(normalize(desc))
    user["description_token_count"] = len(twitter_desc_tokens.intersection(desc_tokens))
    return user


def guess(name, desc):
    query = get_user_search_query(name, desc)
    response = connect_to_endpoint(query)
    if response:
        cleaned_responses = [clean_record(r) for r in response]
        response_features = [extract_features(r, name, desc) for r in cleaned_responses]
        return max(response_features, key=lambda x: x["description_similarity"])

    return None


if __name__ == "__main__":
    with open("authors_clean.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        records = []
        for row in reader:
            user = guess(row["author_name"], row["author_descs"])
            if user:
                row["twitter_handle_guess"] = user["username"]
                row["twitter_id_guess"] = user["id"]
                row["twitter_desc"] = user["description"]
                row["twitter_guess_score"] = user["description_similarity"]
            records.append(row)
    df = pandas.DataFrame.from_records(records)
    df.to_csv("authors_twitter.csv")
