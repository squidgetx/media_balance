import requests
import urllib.parse
import rapidfuzz
import pprint
import time
from datetime import datetime, timedelta
from squidtools import robust_task, util

class APIException(Exception):
    pass

class ArticleFailedException(Exception):
    pass

start_year = 2012
end_year = 2022

def query_nyt_api(qs):
    time.sleep(13)
    # Base URL for the NYT Article Search API
    base_url = f'https://api.nytimes.com/svc/archive/v1/{qs}.json'
    
    # Encode the query parameters
    params = {
        'api-key': API_KEY
    }
    
    # Make the request
    response = requests.get(base_url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        articles = data.get('response', {}).get('docs', [])
        return {'articles': articles}
    else:
        print(f"Error: {response.status_code}")
        raise APIException


qss = []
for y in range(2012, 2023):
    for m in range(1, 13):
        qs = f"{y}/{m}"
        qss.append(qs)

robust_task.robust_task(qss, query_nyt_api, progress_name='archive_progress.json')
