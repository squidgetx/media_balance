import csv
import os
import argparse
import json

from squidtools import robust_task, gpt_utils_async, util

class SourceExtractionFailedException(Exception):
    pass

MAX_ATTEMPTS = 5
SKIP_EXISTING = True

EXTRACT_SYSTEM = """
You are a research assistant whose task it is to extract quotes and other external information 
used by journalists in news articles.

The user will provide the text of a news article.

Generate a numbered list of all quotes and external information attributed to specific people, organizations, or 
documents such as studies, reports, or press releases. Format your response as follows:

1. Rephrase the quote or information in your own words
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
Finally also include comments about the primary source's role and contribution in the article.

Format your response as JSON array with keys "person_name", "person_title", "organization", "document", "category" and "comments"

"""

def make_paragraphs(f):
    # Clean lines here

    def detect(line):
        BLACKLIST = ['CREDIT', 'PHOTOGRAPH', 'wsj', 'latimes', 'Source URL', 'Credit:', 'contributed reporting', 'USA TODAY', 'More:', 'Read This:', "chicagotribune", "NYT", "Continue reading", "Caption", 'nytimes', "WATCH"]
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

# Return a tuple of the sources object and the cost
async def extract_sources(lines, attempt=1):
    article_text = "\n".join(lines)
    result = await gpt_utils_async.system_prompt(
        prompt=EXTRACT_SYSTEM, 
        input=article_text,
        model='gpt-4-1106-preview',
        temp=0.3
    )
    if len(result[0]) < 10:
        # GPT randomly did not finish generating
        # Try up to 3 times
        util.print_err(f"Source Extraction returned a short result... ({attempt}) ({result[0]})")
        raise SourceExtractionFailedException
    return result


async def agg_and_categorize(sources):
    return await gpt_utils_async.system_prompt(AGG_SYSTEM, sources, model='gpt-4-1106-preview', temp=0.3)

async def get_json(sources):
    return await gpt_utils_async.json_prompt_system(JSON_SYSTEM, sources, model='gpt-4-1106-preview', temp=0.3)

async def extract_sources_pipeline(lines):
    sources, cost_extract = await extract_sources(lines)
    if "No sources mentioned" in sources:
        return {
            'sources': [],
            'cost': cost_extract,
            'intermediate_output': {
                'raw': sources
            }
        }
    deduped, cost_dups = await agg_and_categorize(sources)
    if deduped.strip() == '':
        util.print_err("No sources found")
        util.print_err(sources)
        return {
            'sources': [],
            'cost': cost_extract + cost_dups,
            'intermediate_output': {
                'raw': sources
            }
        }
 
    try:
        serialized, cost_json = await get_json(deduped)
    except json.decoder.JSONDecodeError as e:
        util.print_err(f"JSON error:\n  sources: {sources}\n   deduped: {deduped}")
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

async def extract_sources_file(id, filename):
    with open(filename, "rt") as f:
        lines = make_paragraphs(f)
        results = await extract_sources_pipeline(lines)
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
        files = {row['filename']: row['textfile'] for row in reader}
        bad_files = set()
        for id in files:
            try:
                with open(files[id], 'rt') as f:
                    lines = make_paragraphs(f) 
                    if len(lines) == 0:
                        bad_files.add(id)
            except:
                pass

        if len(bad_files) > 0:
            util.print_err(f"Warning: {len(bad_files)} empty files removed from processing")
            for id in bad_files:
                del(files[id])

        results = robust_task.async_robust_task(
            files, extract_sources_file, progress_name = 'sources.progress.json',
            timeout=90)
        print(json.dumps(results, indent=4))
        avg_cost = sum([results[r]['cost'] for r in results])/len(files)
        util.print_err(f"Average cost: {avg_cost}")
