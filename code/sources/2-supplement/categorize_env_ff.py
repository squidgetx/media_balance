from squidtools import sqllm
infile = 'env.or.ff.tsv'
outfile = 'env.or.ff.cat.tsv'

sqllm.apply_files(infile, outfile, {
    'model': 'gpt-4o-mini',
    'input_columns': ['name', 'desc'],
    'output_columns': ['env_category'],
    'prompt': """
        You are an expert research assistant. 
        The user will provide the name and description of an advocacy or business organization. 
        Categorize the organization as 
        "environmental", for environmental, sustainability, conservation, and climate action groups, 
        "fossil fuel", for coal, gas, oil, mining, etc. groups,
        "other" for everything else.
        Format your response as JSON using the key 'env_category'
    """
})