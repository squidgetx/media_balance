import json
import pandas as pd
import re

HS_KEYWORDS = ["high school", "high"]
# Top 25 US news world report universities
# Top 10 liberal arts coleges
# oxford cambridge and LSE
ELITE_KEYWORDS = [
    "harvard",
    "princeton",
    "yale",
    "brown",
    "cornell",
    "dartmouth",
    "upenn",
    "university of pennsylvania",
    "columbia",
    "mit",
    "massachusetts institute of technology",
    "m.i.t.",
    "duke",
    "johns hopkins",
    "jhu",
    "uchicago",
    "university of chicago",
    "caltech",
    "california institute of technology",
    "emory",
    "northwestern",
    "vanderbilt",
    "rice",
    "lse",
    "berkeley",
    "ucla",
    "california los angeles",
    "georgetown",
    "carnegie mellon",
    "ann arbor",
    "nyu",
    "new york university",
    "london school",
    "oxford",
    "cambridge",
    "stanford",
    "pomona",
    "amherst college",
    "swarthmore",
    "haverford",
    "williams",
    "wellesley",
    "bowdoin",
    "carleton",
    "middlebury",
]

JOURNALIST_KEYWORDS = [
    "journal",
    "times",
    "reporter",
    "magazine",
    "media",
    "correspondent",
    "writer",
    "contributor",
    "press",
    "post",
    "news",
]

MSM_KEYWORDS = [
    "new york times",
    "nyt",
    "washington post",
    "cnn",
    "fox",
    "wall street journal",
]


def parse_educ(educ):
    # check high school
    normalized = " ".join(educ).lower()
    is_high_school = any((match in normalized for match in HS_KEYWORDS))

    # check elite
    is_elite = any((match in normalized for match in ELITE_KEYWORDS))

    # get total years
    range_re = re.compile(".*(\d\d\d\d).+(\d\d\d\d)")
    range = next((range_re.match(e) for e in educ if range_re.match(e)), None)
    start_yr = 0
    end_yr = 0
    if range is not None:
        start_yr = int(range[1])
        end_yr = int(range[2])
    return {
        "is_high_school": is_high_school,
        "is_elite": is_elite,
        "start": start_yr,
        "end": end_yr,
    }


def parse_educs(educs):
    # take an array of linkedin / unstructured education objects and
    # return something nice
    if len(educs) == 0:
        return {"total_years": None, "elite": None}
    educs = [parse_educ(e) for e in educs]
    non_hs_educs = [e for e in educs if not e["is_high_school"]]
    total_years = sum([e["end"] - e["start"] for e in non_hs_educs])
    elite = any((e["is_elite"] for e in educs))

    candidate_years = [e["start"] for e in non_hs_educs if e["start"]]
    candidate_years.extend([e["end"] for e in educs if e["is_high_school"]])
    guess_hs_grad_yr = min(candidate_years) if len(candidate_years) > 0 else None

    return {"total_years": total_years, "elite": elite, "hs_grad_yr": guess_hs_grad_yr}


def parse_experience(exp):
    # is it a journa
    normalized = " ".join(exp).lower()
    is_journalist = any((match in normalized for match in JOURNALIST_KEYWORDS))
    is_msm = any((match in normalized for match in MSM_KEYWORDS))
    range_re = re.compile("(?:\w\w\w\s)?(\d\d\d\d)\s-\s(?:\w\w\w\s)?(\d\d\d\d|Present)")
    yrs_re = re.compile(".*?(?:(\d+) yr[s]?)")
    mos_re = re.compile(".*?(?:(\d+) mo[s]?)")
    range = next((range_re.match(e) for e in exp if range_re.match(e)), None)
    start = None
    end = None
    if range is not None:
        start = int(range[1])
        end = 2023 if (range[2] == "Present") else int(range[2])
    yrs = next((yrs_re.match(e) for e in exp if yrs_re.match(e)), None)
    mos = next((mos_re.match(e) for e in exp if mos_re.match(e)), None)
    duration = None
    if yrs or mos:
        n_yrs = int(yrs[1]) if yrs else 0
        n_mos = int(mos[1]) if mos else 0
        duration = n_yrs + n_mos / 12
    return {
        "is_journalist": is_journalist,
        "is_msm": is_msm,
        "start": start,
        "end": end,
        "duration": duration,
    }


def parse_experiences(exps):
    # career journalist?
    # number of years working
    # local paper?

    # how do deal with time as both?
    # maybe we just mark it as part time
    # so the output is:
    # yrs_full_time_journo
    # yrs_full_time_not_journo
    # yrs_part_time_split
    if len(exps) == 0:
        return {
            "exp_yrs_journoTRUE": None,
            "exp_yrs_journoFALSE": None,
            "exp_yrs_journoMIX": None,
            "exp_yrs_msmTRUE": None,
            "exp_yrs_msmFALSE": None,
            "exp_yrs_msmMIX": None,
        }
    parsed = [parse_experience(e) for e in exps]
    years_j = dedup_robust(parsed, "is_journalist")
    years_m = dedup_robust(parsed, "is_msm")
    return {
        "exp_yrs_journoTRUE": years_j["n1"],
        "exp_yrs_journoFALSE": years_j["n0"],
        "exp_yrs_journoMIX": years_j["nb"],
        "exp_yrs_msmTRUE": years_m["n1"],
        "exp_yrs_msmFALSE": years_m["n0"],
        "exp_yrs_msmMIX": years_m["nb"],
    }


def dedup_robust(intervals, key):
    # handle both intervals with and without start dates
    # eg, one entry might only contain a duration
    # and then the next might have a start and end date
    # We can't do better than just assuming that raw durations
    # are exclusive, sorry :(
    with_start_end = [i for i in intervals if i["start"] and i["end"]]
    results = dedup(with_start_end, key)
    duration_only = [
        i
        for i in intervals
        if i["duration"] and i["start"] is None and i["end"] is None
    ]
    for i in duration_only:
        if i[key]:
            results["n1"] += i["duration"]
        else:
            results["n0"] += i["duration"]
    return results


def dedup(intervals, key):
    # given an array with start and end times that may overlap
    # and the name of a binary key
    # return total time spent for each state of the binary key
    # example input:
    # 2004 - 2006, key = 1
    # 2005 - 2007, key = 0
    # > years_1: 1
    # > years_0: 1
    # > years_split: 1
    intervals.sort(key=lambda e: e["start"])
    years = {}

    for interval in intervals:
        for y in range(interval["start"], interval["end"]):
            if y not in years:
                years[y] = set()

            years[y].add(interval[key])
    # at the end, count em up
    n0 = 0
    n1 = 0
    nb = 0
    for y in years:
        if True in years[y] and False in years[y]:
            nb += 1
        elif True in years[y]:
            n1 += 1
        else:
            n0 += 1

    return {"n1": n1, "n0": n0, "nb": nb}


def guess_gender(j):
    desc = j.get("desc", "")
    if j.get("about"):
        desc += j["about"]
    n_she = desc.count(" she ") + desc.count("She ")
    n_he = desc.count(" he ") + desc.count("He ")
    n_they = desc.count("they")
    if n_she == 0 and n_he > 0:
        return "M"
    if n_he == 0 and n_she > 0:
        return "F"
    if n_he == 0 and n_she == 0 and n_they > 0:
        return "NB"
    return None


def patch(j):
    # Try to fill in any blanks when there is no linkedin data
    desc = j["desc"]
    elite_educ = any((m in desc.lower() for m in ELITE_KEYWORDS))
    educ = any((m in desc.lower() for m in ["college", "university", "school"]))

    # If the bio doesn't talk about education at all we can't conclude anything
    if elite_educ == False and educ == False:
        elite_educ = None

    return {"elite": elite_educ}


JSON = "tmp/4.json"
journalists = json.load(open(JSON))
records = []
for j in journalists:
    educs = parse_educs(j.get("education", []))
    exps = parse_experiences(j.get("experience", []))
    journo = {
        "name": j["name"],
        "hostname": j["hostname"],
        "linkedin": j.get("url"),
        "twitter": j.get("twitter"),
        "news_url": j.get("link"),
        "gender": guess_gender(j),
    }
    journo.update(educs)
    journo.update(exps)
    if j["linkedin"] is None:
        journo = patch(journo)
    records.append(journo)

pd.DataFrame.from_records(records).to_csv("journalists.tsv", sep="\t")
