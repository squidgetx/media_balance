from squidtools import sqllm
infile = '../3-dime/politicians/sources.dime.orgs.pols.tsv'
outfile = 'sources.comments.tsv'

sqllm.apply_files(infile, outfile, {
    'model': 'gpt-4o-mini',
    "input_columns": ["comments"], 
    "output_columns": ["comment.explanation", "comment.category"], 
    'temp': 0,
    'prompt': """
       You are an expert research assistant. 
       Categorize the user provided text about climate change.
       Business: commercial impact, energy industry, financial costs, new technologies, etc.
       Environment: environmental impact, need for urgent action, etc.
       Policy: government or politician actions, plans, policies, etc.
       Other: everything else
       Explain yourself before giving a category. 
       Format your response as JSON with keys "comment.explanation" and "comment.category", 
    """
})