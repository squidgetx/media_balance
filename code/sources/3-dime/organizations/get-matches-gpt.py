from squidtools import sqllm
infile = 'maybes.bert.stg1.tsv'
outfile = 'matches.gpt.stg2.tsv'

sqllm.apply_files(infile, outfile, {
    'model': 'gpt-4o',
    'input_columns': ['name', 'organization'],
    'output_columns': ['explanation', "relation"],
    'temp': 0,
    'prompt': """
        The user will provide the names of two organizations.
        Explain their relation to each other.
        Then, categorize their relation as either "match" or "not related"
        Organizations match if they are the same organization or branches of the same parent organization.
        Format your response as JSON with the keys "explanation" and "relation"    
    """
})