import openai
import csv
import os
import time
import argparse
import json
import sys


from squidtools import robust_task, gpt_utils

openai.api_key = os.environ["OPENAI_KEY"]

MAX_ATTEMPTS = 5
SKIP_EXISTING = True

EXTRACT_SYSTEM = """
You are a research assistant whose task it is to extract quotes and other external information 
used by journalists in news articles.

The user will provide the text of a news article.

Generate a numbered list of all quotes and external information attributed to specific people, organizations, or 
documents such as studies, reports, or press releases. Format your response as follows:

1. Quote or information
- Name of the source
- Background of the source

Some articles do not mention any information drawn from external sources. 
In these cases, simply say "No sources mentioned."
"""

AGG_SYSTEM = """
You are a research assistant whose task it is to understand the sources of quotes and other external information used by journalists in writing news. 

The user will provide a list of quotes and external information referenced in a news article.

Aggregate together the quotes and information drawn from the same sources into a new numbered list. 
Provide a description of the source, a summary of the source's contribution, and a categorization of "politician", "bureaucrat", "nonprofit/activist", "academic", "industry/corporation", "lobbyist/interest group", "media/author", "religious leader", or "citizen." 
Format the list as follows:

Name of the source
- Description of the source
- Summary of the source's contribution
- Documents authored by the source, if relevant
- Category
"""

CATEGORIZE_SYSTEM = """
You are a research assistant whose task it is to categorize the primary sources used by journalists in writing news. 

The user will provide a list of primary sources and their contributions to a news article. 

For each source, summarize their contribution to the article, provide a description of the source, then apply a categorization of 
"politician", 
"bureaucrat", 
"judge",
"international organization",
"military",
"lobbyist/interest group",
"nonprofit/activist", 
"academic", 
"nonacademic expert/research",
"industry/corporation", 
"lobbyist/interest group", 
"media/author", 
"healthcare/medical",
"religious leader", 
"citizen," or
"other."
     
"""



JSON_SYSTEM = """
For each entry in the given list of primary sources, identify the person's name (if the source is a person), their title (such as President, Professor, Spokesman, etc.), 
the organization name, concise description of associated written document if any (eg, study published in Nature, data from 2014, etc.), and the category (already provided). 

If any of these are not relevant provide a value of N/A. For unnamed or anonymous people provide a best guess at their title. 
Do not include titles in the person name field (eg, Barack Obama instead of President Obama). 
Finally also include comments about the primary source's role in the article.

Format your response as JSON array with keys "person_name", "person_title", "organization", "document", "category" and "comments"

"""

def get_response(system, content, model='gpt-4-1106-preview'):
    messages = [{
        "role": "system",
        "content": system,
    },{
        "role": "user",
        "content": content
    }]
    response = gpt_utils.generate_chat_response(messages, model=model, temperature=0.3)
    cost = gpt_utils.get_total_cost([response])
    text = gpt_utils.get_message_text(response)
    return text, cost

# Return a tuple of the sources object and the cost
def extract_sources(lines):
    article_text = "\n".join(lines)
    return get_response(EXTRACT_SYSTEM, article_text)

def categorize_sources(sources):
    return get_response(CATEGORIZE_SYSTEM, sources, model='gpt-4-1106-preview')

def agg_and_categorize(sources):
    return get_response(AGG_SYSTEM, sources, model='gpt-4-1106-preview')

def get_json(sources):
    return get_response(JSON_SYSTEM, sources, model='gpt-4-1106-preview')

def make_paragraphs(f):
    # Clean lines here

    def detect(line):
        BLACKLIST = ['CREDIT', 'PHOTOGRAPH', 'wsj', 'latimes', 'Source URL', 'Credit:', 'contributed reporting', 'USA TODAY', 'More:', 'Read This:', "NYT", "Continue reading", "Caption", 'nytimes', "WATCH"]
        for kw in BLACKLIST:
            if kw in line:
                return True
        return False

    paras = []

    for line in f:
        line = line.strip()
        if line == '':
            continue
        if detect(line):
            continue
        paras.append(line)
        
    return paras

def extract_sources_pipeline(lines):
    sources, cost_extract = extract_sources(lines)
    if "No sources mentioned" in sources:
        return {
            'sources': [],
            'cost': cost_extract,
            'intermediate_output': {
                'raw': sources
            }
        }
    deduped, cost_dups = agg_and_categorize(sources)
    #categorized, cost_categorize = categorize_sources(deduped)
    json_sources, cost_json = get_json(deduped)
    serialized = None
    try: 
        response = json_sources.replace('```json', '').replace('```', '').strip()
        serialized = json.loads(response)
    except json.decoder.JSONDecodeError as e:
        print("json decode error: ")
        print(json_sources)
        raise e
    return {
        'sources': serialized,
        'cost': cost_extract + cost_json + cost_dups,
        'intermediate_output': {
            'raw': sources,
            'agged_categorized': deduped,
            'costs': [cost_extract, cost_json, cost_dups]
        }
    }

def extract_sources_file(filename):
    with open(filename, "rt") as f:
        lines = make_paragraphs(f)
        results = extract_sources_pipeline(lines)
        results['filename'] = filename
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Use ChatGPT to extract the journalist's sources from a plaintext news article."
    )
    parser.add_argument(
        "tsv",
        type=str,
        help="Path to the TSV file used to store textfiles to get sources for"
    )

    args = parser.parse_args()
    tsvfile = args.tsv
    with open(tsvfile, 'rt') as tf:
        reader = csv.DictReader(tf, delimiter='\t')
        os.chdir(os.path.dirname(tsvfile))
        files = [row['filename'] for row in reader]
        results = robust_task.robust_task(files, extract_sources_file, progress_name = 'sources.progress.json')
        print(json.dumps(results, indent=4))
        avg_cost = sum([results[r]['cost'] for r in results])/len(files)
        print(f"Average cost: {avg_cost}")
