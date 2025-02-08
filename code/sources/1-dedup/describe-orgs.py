from squidtools import sqllm
infile = 'orgs.raw.tsv'
outfile = 'orgs.descriptions.tsv'

sqllm.apply_files(infile, outfile, {
    'model': 'gpt-4o-mini',
    'input_columns': ['organization', 'category.clean', 'persons'],
    'output_columns': ['organization_name', 'organization_description'],
    'prompt': """
        You are an expert research assistant. 
        The user will provide some information about an organization.
        Provide a the full name of the organization and
        then a one sentence general description of the organization that
        includes common alternative names.
        Format your response as JSON using the keys 'organization_name', 'organization_description' 
    """
})