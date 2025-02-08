from squidtools import gpt_utils_async, robust_task, util
import math
import sys

anchors = [
    {"name": "greenpeace", "cfscore": -1.49},
    {
        "name": "sierra club",
        "cfscore": -0.96,
    },
    {
        "name": "national wildlife federation",
        "cfscore": -0.6,
    },
    {
        "name": "the nature conservancy",
        "cfscore": -0.32,
    },
    {"name": "center", "cfscore": 0.0},
    {
        "name": "national association of homebuilders",
        "cfscore": 0.36,
    },
    {"name": "shell", "cfscore": 0.6},
    {"name": "national mining association", "cfscore": 0.94},
    {"name": "institute for energy research", "cfscore": 2.6},
]

test_cases = [
    {"name": "union of concerned scientists", "cfscore": -1.1},
    {
        "name": "audobon society",
        "cfscore": -0.8,
    },
    {"name": "facebook", "cfscore": -0.15},
    {
        "name": "united airlines",
        "cfscore": 0.15,
    },
    {"name": "national association of homebuilders", "cfscore": 0.36},
    {"name": "exxon", "cfscore": 0.6},
]


def get_cmp_entry(cmp_i):
    return anchors[math.floor(len(anchors) / 2 + cmp_i)]


async def ask_left_right(org, cmp_i):
    org_name = org["organization_name"]
    org_desc = org["description"]
    cmp = get_cmp_entry(cmp_i)
    cmp_name = cmp["name"]

    prompt = f"""
In the context of politics and ideology, is {org_name} considered left or right of {cmp_name}?
{org_desc}

Explain yourself before answering. 
Format your response as JSON with the keys "explanation" and "response": "left"/"right"/"same"
"""
    response, cost = await gpt_utils_async.json_prompt_system(
        "You are an expert assistant",
        prompt,
        model="gpt-4o",
        temp=0.5,
    )
    return response
    
async def ask_lr(org, min=-4, max=4):
    cmp_i = math.floor((min + max) / 2)
    if min == max:
        return min
    if abs(min - max) == 1:
        return (min + max) / 2

    response = await ask_left_right(org, cmp_i)
    position = response.get("response", "").lower()

    if position == "left":
        return await ask_lr(org, min=min, max=cmp_i)
    elif position == "right":
        return await ask_lr(org, min=cmp_i, max=max)
    elif position == "same":
        return cmp_i
    else:
        # GPT refused to categorize
        # Most of the time this is actually fine because the group cannot be
        # categorized. So we are OK to leave this as NA in the final output data
        util.print_err(response)
        raise Exception


async def ask_lr_layer(org_name, org):
    i = await ask_lr(org)
    i2 = await ask_lr(org, math.floor(i - 2), math.ceil(i + 2))
    return {
        "rank1": i,
        "rank2": i2,
        "rank": (i + i2) / 2,
        #'cfscore': get_ideo((i + i2) / 2)
    }


def get_ideo(cmp_i):
    if cmp_i == int(cmp_i):
        return get_cmp_entry(cmp_i)["cfscore"]
    else:
        a = get_cmp_entry(math.floor(cmp_i))["cfscore"]
        b = get_cmp_entry(math.floor(cmp_i) + 1)["cfscore"]
        fr = 1 - abs(cmp_i - math.floor(cmp_i))
        result = a * fr + b * (1 - fr)
        return result


infile = sys.argv[1]
outfile = sys.argv[2]
records = util.read_delim(infile)
input_records = {}
for r in records:
    input_records[r["organization_name"]] = r
results = robust_task.async_robust_task(
    input_records, ask_lr_layer, "impute-pairs.progress.json", timeout=60
)
for r in results:
    input_records[r].update(results[r])
util.write_tsv(input_records.values(), outfile)
