import openai
import os
import argparse
import json

openai.api_key = os.environ["OPENAI_KEY"]

MAIN_PROMPT = """Concisely summarize the following article. Preserve quotations and opinions attributed to specific people, organizations, or documents in a list at the end of the summary."""

EXTRACT_PROMPT = """
    Given the following summary of a news article and the main quotations and sources, return a JSON array of the organizations and people quoted in the article. 
    Include "name", "organizational affiliation", "title", and "category". 
    Organization affiliations are the names of the affiliated company, agency, nonprofit, think tank, university, etc. if any.
    Examples of "title" are "Governor of Nebraska", "CEO", "Executive Director", "Professor", etc.
    Examples of "category" are "politician", "bureaucrat", "nonprofit/activist", "academic", "industry/corporation", "lobbyist/interest group", "media/author", "religious leader", "citizen".
"""

INPUT_COST = 0.0015 / 1000
OUTPUT_COST = 0.002 / 1000


def summarize_article(text):
    messages = [
        {
            "role": "system",
            "content": """
Use the following step-by-step instructions to respond to user inputs.

Step 1 - The user will provide you with a news article. Concisely summarize the article with a prefix that says "Summary: ".

Step 2 - Provide a list of quotations and opinions attributed to specific people, organizations, or documents in the article with a prefix that says "Quotations: ".
For each list item include the source's name and important context.
        """,
        },
        {"role": "user", "content": text},
    ]
    return generate_chat_response(messages)


def extract_from_summary(summary):
    messages = [{"role": "user", "content": f"{EXTRACT_PROMPT}\n{summary}"}]
    return generate_chat_response(messages)


# Return a tuple of the sources object and the cost
def extract_sources(text):
    response = summarize_article(text)
    response2 = extract_from_summary(get_message_text(response))
    sources = json.loads(get_message_text(response2))
    return sources, get_total_cost([response, response2])


# utility functions for handling open AI responses


def generate_chat_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response


def get_message_text(response):
    return response.choices[0].message.content


def get_total_tokens(responses):
    return sum([r.usage.total_tokens for r in responses])


def get_total_cost(responses):
    return sum(
        [
            r.usage.prompt_tokens * INPUT_COST + r.usage.completion_tokens * OUTPUT_COST
            for r in responses
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file.")
    parser.add_argument("filename", type=str, help="Path to the file")

    args = parser.parse_args()
    filename = args.filename
    with open(filename, "rt") as f:
        text = "\n".join([lines.strip() for lines in f])
        sources, cost = extract_sources(text)
        print(sources)
        print(f"Cost: ${cost})
