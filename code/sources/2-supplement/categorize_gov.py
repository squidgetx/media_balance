from squidtools import sqllm
infile = 'gov.sources.tsv'
outfile = 'gov.sources.cat.tsv'

sqllm.apply_files(infile, outfile, {
    'model': 'gpt-4o-mini',
    'input_columns': ['entity_name', 'entity_desc'],
    'output_columns': ['gov_category'],
    'prompt': """
        You are an expert research assistant. 
        The user will provide the name and description of a government organization. 
        Categorize the organization as 
        "US politician", for legislative and executive bodies, 
        "US bureaucrat" for government agencies and offices, 
        "US other government" for other US government related bodies, 
        "Intergovernmental" for bodies like the UN or WHO, and
        "Non-US" for government bodies in other countries.
        Format your response as JSON using the key 'gov_category'
    """
})