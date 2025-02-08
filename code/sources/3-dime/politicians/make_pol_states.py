from squidtools import sqllm
infile = 'politicians.tsv'
outfile = 'politicians.states.tsv'

sqllm.apply_files(infile, outfile, {
    'model': 'gpt-4o-mini',
    'input_columns': ['person_name', 'titles', 'organizations'],
    'output_columns': ['state'],
    'temp': 0,
    'prompt': """
        Provide the state most affiliated with the given politician.
        Respond with a JSON object using the key "state". 
        Use the state abbreviation (CA, AL, AK, etc) and "NA" if the 
        politician is not a US politician.
    """
})