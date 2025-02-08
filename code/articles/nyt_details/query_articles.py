import requests
import urllib.parse
import rapidfuzz
import pprint
import time
from datetime import datetime, timedelta
from squidtools import robust_task, util

# # Replace 'YOUR_API_KEY' with your NYT API key
API_KEY='58JuxwAhL6m69czgJdXjheGpLwVh4UH9'

class APIException(Exception):
    pass

class ArticleFailedException(Exception):
    pass

def query_nyt_api(title, start_date, end_date):
    # Base URL for the NYT Article Search API
    base_url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
    
    # Encode the query parameters
    params = {
        'q': title,
        'begin_date': start_date.replace('-', ''),
        'end_date': end_date.replace('-', ''),
        'api-key': API_KEY
    }
    
    # Make the request
    response = requests.get(base_url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        articles = data.get('response', {}).get('docs', [])
        return articles
    else:
        print(f"Error: {response.status_code}")
        raise APIException

def query_nyt_api_retry(title, start_date, end_date, attempt = 0):
    if attempt > 3:
        return ArticleFailedException
    try: 
        return query_nyt_api(title, start_date, end_date)
    except APIException:
        ts = pow(2, attempt + 2)
        util.print_err(f"API failed: sleeping for {ts}")
        time.sleep(ts)
        return query_nyt_api_retry(title, start_date, end_date, attempt+1)

def query_article(title, date):
    date_obj = datetime.fromisoformat(date)

    # Calculate 7 days before and after
    date_before = date_obj - timedelta(days=7)
    date_after = date_obj + timedelta(days=7)

    start_date = date_before.strftime("%Y-%m-%d")
    end_date = date_after.strftime("%Y-%m-%d")

    results = query_nyt_api_retry(title, start_date, end_date)

    # Print the articles if found
    for article in results:
        result_headline = article['headline']['main']
        sim = rapidfuzz.fuzz.ratio(title, result_headline, processor = rapidfuzz.utils.default_process)
        if sim > 95:
            return article
    return {
        'error': 'No match found'
    }

articles = util.read_delim('articles.tsv', 'filename')
    
def query_article_filename(filename):
    title = articles[filename]['title']
    date = articles[filename]['date']
    return query_article(title, date)

robust_task.robust_task(
    list(articles),
    query_article_filename,
)
