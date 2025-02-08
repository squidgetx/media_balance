from squidtools import sqllm
import argparse

IDENTIFY_PROMPT = """
Based on the provided excerpt, does the news article primarily discuss
government policy, legislation, plans, or proposals related to climate change
(emissions regulations, energy subsidies, natural resource regulations, infrastructure plans, etc.)? 
Explain yourself before answering,
Format your answer as JSON with keys "explanation" with the explanation,
and "policy_label_gpt" with values "TRUE" or "FALSE".
"""

parser = argparse.ArgumentParser()
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()

sqllm.apply_files(args.infile, args.outfile, {
    'model': 'gpt-4o-mini',
    'input_columns': ['excerpt'],
    'output_columns': ['policy_label_gpt'],
    'prompt': IDENTIFY_PROMPT
})
