import openai
from openai import error
import csv
import os
import time
import argparse
import json
import sys

from squidtools import robust_task

openai.api_key = os.environ["OPENAI_KEY"]

MAX_ATTEMPTS = 5
SKIP_EXISTING = True

IDENTIFY_PROMPT = """
Does the following excerpt contain any information or statements attributed to a person, organization, or document (such as a study, report, or press release)? Be concise.
"""

SUMMARIZE_PROMPT = """
Summarize the following news article. 
"""

EXTRACT_PROMPT = """
    Given the following summary and excerpts from a news article make a list with one entry for each excerpt.
    Include the name of the person, document, or organization that is used as a source in the excerpt,
    the person's title where relevant ("Governor of Nebraska", "CEO", "Executive Director", "Professor", "Spokesman" etc.),
    organizational affiliations where relevant,
    and the category. 
    Examples of "category" are "politician", "bureaucrat", "nonprofit/activist", "academic", "industry/corporation", "lobbyist/interest group", "media/author", "religious leader", "citizen".
"""

JSON_PROMPT = """
    Given the following list of source names, organizations, and titles, 
    remove duplicates and then
    convert it to a JSON array with keys "name", "organization", "title", "type", and "category"
    where "type" is one of "person", "organization", or "document"
"""

CLEAN_JSON_PROMPT = """
Clean up the following JSON array. 
Remove duplicate entries, usually where an organization is listed when the 
array already has a spokesperson for that organization listed as a separate entry.
"""


def manual_test(line):
    if "said" in line:
        return True
    if '"' in line:
        return True
    if "“" in line:
        return True
    if "according to" in line.lower():
        return True
    return False


def extract_quotes(lines):
    # For each line in the article, run a request to GPT asking if it is attributed to a source
    quotes = []
    responses = []
    for line in lines:
        # don't bother with excerpts that are obvious
        # Surprisingly, GPT sometimes misses these anyyway.
        if manual_test(line):
            quotes.append(line)
            continue
        response = basic_prompt(IDENTIFY_PROMPT, line)
        is_quote = "No" not in get_message_text(response)
        if is_quote:
            quotes.append(line)
            responses.append(response)

    return quotes, responses


def make_list(summary, lines):
    N_ITER = 2
    list = ""
    excerpts, all_responses = extract_quotes(lines)
    extract_input = create_extract_input(summary, excerpts)
    print(extract_input)
    for _ in range(N_ITER):
        list_response = basic_prompt(EXTRACT_PROMPT, extract_input, big_context=True)
        all_responses.extend([list_response])
        list += get_message_text(list_response)

    print(list)
    return list, all_responses


# Return a tuple of the sources object and the cost
def extract_sources(lines):
    summary_response = basic_prompt(
        SUMMARIZE_PROMPT, "\n".join(lines), big_context=True
    )
    list, responses = make_list(get_message_text(summary_response), lines)
    json_response = basic_prompt(JSON_PROMPT, list)

    sources_clean_response = basic_prompt(
        CLEAN_JSON_PROMPT, get_message_text(json_response)
    )
    sources = json.loads(get_message_text(sources_clean_response))
    responses.extend([summary_response, json_response, sources_clean_response])

    return sources, get_total_cost(responses)


def create_extract_input(summary, excerpts):
    joined_excerpts = "\n".join(excerpts)
    return f"""
    Summary:
    {summary}

    Excerpts:
    {joined_excerpts}
    """


# utility functions for handling open AI responses


def basic_prompt(prompt, input, big_context=False):
    messages = [{"role": "user", "content": f"{prompt}\n{input}"}]
    return generate_chat_response(messages, big_context)


def generate_chat_response(messages, big_context=False, attempt=0):
    if big_context:
        model = "gpt-3.5-turbo-16k"
    else:
        model = "gpt-3.5-turbo"
    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=0.5,
            messages=messages,
        )
        return response
    except error.ServiceUnavailableError as e:
        attempt += 1
        if attempt > MAX_ATTEMPTS:
            raise e

        sleeptime = pow(2, attempt + 1)
        sys.stderr.write("Service Unavailable.. sleeping for " + str(sleeptime) + "\n")
        sys.stderr.flush()
        time.sleep(sleeptime)
        return generate_chat_response(messages, big_context, attempt)
    except error.APIError as e:
        if "bad gateway" in str(e).lower():
            # bad gateway, we retry
            attempt += 1
            if attempt > MAX_ATTEMPTS:
                raise e
            sleeptime = pow(2, attempt + 1)
            print(f"Bad Gateway. Sleeping for {sleeptime}s.")
            time.sleep(sleeptime)
            return generate_chat_response(messages, big_context, attempt)
        else:
            raise e


def get_message_text(response):
    return response.choices[0].message.content


def get_total_tokens(responses):
    return sum([r.usage.total_tokens for r in responses])


def get_total_cost(responses):
    input_costs = {
        "gpt-3.5-turbo-0613": 0.0015 / 1000,
        "gpt-3.5-turbo-16k-0613": 0.003 / 1000,
    }
    output_costs = {
        "gpt-3.5-turbo-0613": 0.002 / 1000,
        "gpt-3.5-turbo-16k-0613": 0.004 / 1000,
    }
    # check if models are present
    for r in responses:
        if r["model"] not in input_costs:
            sys.stderr.write(f"{r['model']} not found in input costs! update please")
            return -1

    return sum(
        [
            r.usage.prompt_tokens * input_costs[r["model"]]
            + r.usage.completion_tokens * output_costs[r["model"]]
            for r in responses
        ]
    )


def make_paragraphs(f):
    text = "\n".join([lines.strip() for lines in f])
    return text.split("\n\n")


def extract_sources_file(filename):
    with open(filename, "rt") as f:
        lines = make_paragraphs(f)
        sources, cost = extract_sources(lines)
        results = {"filename": filename, "sources": sources, "cost": cost}
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
