from squidtools import util
import rapidfuzz
import json

all_articles = []

with open('archive_progress.json', 'rt') as db:
    for line in db:
        data = json.loads(line)
        articles = data['articles']
        for a in articles:
            article_clean = {
                'abstract': a['abstract'],
                'headline': a['headline']['main'],
                'print_headline': a['headline']['print_headline'],
                'pub_date': a['pub_date'],
                'news_desk': a['news_desk'],
                'section_name': a['section_name'],
                'nyt_id': a['_id'],
                'print_section': a.get('print_section'),
                'print_page': a.get('print_page'),
                'web_url': a.get('web_url')
            }
            all_articles.append(article_clean)

util.write_tsv(all_articles, 'nyt_archive.tsv')
