from squidtools import webscraper, robust_task, util

import sys
import random
import time

scraper = webscraper.PlaywrightScraper(delay=1)

def get_comments(url):
    # Has to return a dict - I always forget this...
    # Some custom waiting logic
    coin = random.random()
    if coin < 0.05:
        # sleep for 1-2 minutes
        pass
    #time.sleep(60 * random.random() + 60)

    scraper.nav(url)
    scraper.page.screenshot(path='current-page.png')
    main_div = scraper.find_element("div#app") or scraper.find_element("main#main")
    if main_div is None:
        util.print_err("We got captcha'd! Sleeping for 5-10 minutes")
        #time.sleep(30 * random.random() + 30)
        raise Exception
    main_div.wait_for_element_state('stable')

    n_comments = scraper.find_element_text('[data-testid="comments-speech-bubble-header"]')
    if n_comments is None:
        n_comments = scraper.find_element_text('[data-testid="share-tools"]>>li.commentAdjustClass')
    util.print_err(n_comments)
    return {
        'n_comments': n_comments
    }


records = util.read_delim('articles-with-urls.tsv')
urls = [r['web_url'] for r in records]
random.shuffle(urls)
records = robust_task.robust_task(urls, get_comments, progress_name='url_comment_scraping_progress.json')
util.write_csv(records, 'nyt-comments.tsv')