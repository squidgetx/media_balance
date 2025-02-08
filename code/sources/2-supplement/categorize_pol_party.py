from squidtools import sqllm
infile = 'politicians.tsv'
outfile = 'politicians.parties.tsv'

sqllm.apply_files(infile, outfile, {
    'model': 'gpt-4o-mini',
    'input_columns': ['person_name', 'titles', 'organizations'],
    'output_columns': ['pol_party'],
    'prompt': """
        You are an expert research assistant. 
        The user will provide the name and description of a politician.
        Categorize the political party as "Democrat", "Republican", or "Other
        Format your response as JSON using the key 'pol_party'
    """
})