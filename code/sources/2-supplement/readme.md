# code to supplement the data on sources 

specifically, we want to identify 
- politicians (under government category)
- bureaucrats (under government category)
- fossil fuel groups (in business and advocacy)
- environmental groups (in business and advocacy)
- political parties of the politicians

We use basic gpt prompting to do this.
- categorize_env.py categorizes the fossil fuels and environment groups
- categorize_gov.py categorizes the government groups
- categorize_pol_party.py categorizes the political parties
- validate.R cleans and merges the data
- we manually label ~100 groups to validate all the data


