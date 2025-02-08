"""
Clean and join author data
collected from muckrack and proxycurl/linkedin
"""

import json
import csv
from squidtools import names, util

linkedin_filename = "data/authors.linked.json"
linkedin_redos_filename = "data/authors.linkedin.redos.json"
muckrack_filename = "data/author_muckrack.json"
authors_filename = "data/authors.noop.tsv"

muckrack = json.load(open(muckrack_filename))
linkedin = json.load(open(linkedin_filename))
linkedin_redos = json.load(open(linkedin_redos_filename))
linkedin_clean_supp = json.load(open("data/authors.linkedin.manual.json"))
li_twitter = json.load(open("data/authors.linkedin.twitter.json"))


def parse_education(edus):
    def get_degree_type(field, degree):
        degree_types = {
            "masters": [
                "MA",
                "MFA",
                "MS",
                "MSc",
                "MPA",
                "MDiv",
                "MPhil",
                "Master",
                "master",
            ],
            "postgrad": ["JD", "MBA", "Law", "law"],
            "associates": ["associate", "Associate"],
            "doctorate": [
                "PhD",
                "PHD",
                "Doctor",
                "Graduate",
                "graduate",
                "postgrad",
                "Postgrad",
            ],
            "undergrad": [
                "BFA",
                "BA",
                "AB",
                "BS",
                "BSc",
                "Bachelor",
                "bachelor",
                "Undergraduate",
                "undergrad",
            ],
            "highschool": ["A level", "A Level", "High School"],
        }
        terms = f"{field} {degree}".replace(".", "")
        for dt in degree_types:
            for kw in degree_types[dt]:
                if kw in terms:
                    return dt
        return "other"

    results = {
        "raw": [],
        "has_postgrad": False,
        "undergrad_school": None,
        "undergrad_field": None,
        "undergrad_graduation_year": None,
    }
    for edu in edus:
        start = edu["starts_at"]["year"] if edu["starts_at"] else None
        end = edu["ends_at"]["year"] if edu["ends_at"] else None
        field = edu["field_of_study"]
        degree = edu["degree_name"]
        school = edu["school"]
        deg_type = get_degree_type(field, degree)
        edu_obj = {
            "start": start,
            "end": end,
            "field": field,
            "degree": degree,
            "school": school,
            "len": end - start if end and start else None,
            "deg_type": deg_type,
        }
        if deg_type == "undergrad":
            # We'll fill in 4 year educations here, lol
            if edu_obj["len"] is None:
                edu_obj["len"] = 4
                if edu_obj["start"] is None and edu_obj["end"]:
                    edu_obj["start"] = edu_obj["end"] - 4
                if edu_obj["end"] is None and edu_obj["start"]:
                    edu_obj["end"] = edu_obj["start"] + 4
            if results["undergrad_school"] is None:
                results["undergrad_school"] = edu_obj["school"]
                results["undergrad_field"] = edu_obj["field"]
                results["undergrad_graduation_year"] = edu_obj["end"]
        elif deg_type != "highschool":
            results["has_postgrad"] = True

        results["raw"].append(edu_obj)
    results["num_educations"] = len(results["raw"])
    # results['raw'] = json.dumps(results['raw'])

    return results


def test_is_journo(title, company):
    # Return true if this is a journalistic type of job
    # Use basic keyword logic
    companies = [
        "times",
        "journal",
        "post",
        "media",
        "tribune",
        "news",
        "globe",
        "inquirer",
        "magazin",
        "press",
        "cnn",
        "herald",
        "broadcast",
    ]
    titles = [
        "news",
        "producer",
        "writ",
        "journalis",
        "correspondent",
        "report",
        "editor",
        "bureau chief",
        "critic",
        "columnist",
        "author",
    ]
    for c in companies:
        if company and c in company.lower():
            return True
    for t in titles:
        if title and t in title.lower():
            return True
    print(title, company)
    return False


def clean_spaces(txt):
    if txt is None:
        return None
    return " ".join(txt.split()).strip()


def parse_experiences(exps):
    """
    "experiences": [
      {
        "starts_at": { "day": 1, "month": 3, "year": 2016 },
        "ends_at": null,
        "company": "RCNi",
        "company_linkedin_profile_url": "https://www.linkedin.com/company/rcni/",
        "title": "Editor, Nursing Management and Emergency Nurse journals",
        "description": null,
        "location": null,
        "logo_url": "https://media-exp1.licdn.com/dms/image/C4D0BAQEWAXqT66KnSQ/company-logo_400_400/0/1622110697578?e=1668038400&v=beta&t=F0tC8LJxMBEVANqgLIHX_cFlFfsO20d_Oqh0y4nEfqc"
      },
    """
    # what do we care about?
    # number of newspapers?
    # career journalist vs not career journalist
    records = []
    for i, exp in enumerate(exps):
        start = exp["starts_at"]["year"] if exp["starts_at"] else None
        end = exp.get("ends_at").get("year") if exp["ends_at"] else None
        if end is None and i == 0:
            # Impute null end to mean "current" if it's the first entry
            end = 2024
        title = exp["title"]
        company = exp["company"]
        is_journo = test_is_journo(title, company)
        records.append(
            {
                "start": start,
                "end": end,
                "years": end - start if end and start else None,
                "current": i == 0,
                "title": title,
                "company": company,
                "is_journo": is_journo,
            }
        )
    return records


def update_li(record, li_info, clean_name, li_lookup_src):
    if li_info is None:
        return record
    if "public_identifier" not in li_info:
        record["linkedin_error"] = f"{li_lookup_src} failed"
    else:
        record["linkedin_id"] = li_info["public_identifier"]
        record["linkedin_url"] = f"https://www.linkedin.com/in/{record['linkedin_id']}"
        record["gender"] = li_info.get("gender")
        record["tw_url"] = (
            li_info["extra"].get("twitter_profile_id") if li_info.get("extra") else None
        )
        record["first_name"] = clean_spaces(li_info["first_name"])
        record["last_name"] = clean_spaces(li_info["last_name"])
        record["full_name"] = clean_spaces(li_info["full_name"])
        record["occupation"] = clean_spaces(li_info["occupation"])
        record["headline"] = clean_spaces(li_info["headline"])
        record["summary"] = clean_spaces(li_info["summary"])
        record["country"] = li_info["country_full_name"]
        record["city"] = li_info["city"]
        record["state"] = li_info["state"]
        record["li_connections"] = li_info["connections"]
        edu = parse_education(li_info["education"])
        record["edu.has_postgrad"] = edu["has_postgrad"]
        record["edu.undergrad"] = clean_spaces(edu["undergrad_school"])
        record["edu.field"] = edu["undergrad_field"]
        record["edu.grad_year"] = edu["undergrad_graduation_year"]
        record["edu.school_names"] = clean_spaces(
            ",".join([e["school"] for e in edu["raw"] if e["school"]])
        )
        record["edu.n_entries"] = edu["num_educations"]
        exp = parse_experiences(li_info["experiences"])
        record["exp.recent_company"] = (
            clean_spaces(exp[0]["company"]) if len(exp) else None
        )
        record["exp.recent_title"] = clean_spaces(exp[0]["title"]) if len(exp) else None
        exp.sort(key=lambda x: x['start'] if x['start'] else 9999)
        record["exp.companies"] = ",".join(
            [clean_spaces(e["company"]) for e in exp if e["company"]]
        )
        record["exp.titles"] = ",".join(
            [clean_spaces(e["title"]) for e in exp if e["title"]]
        )
        record["exp.n_entries"] = len(exp)
        # We assume that people are always working from the beginning of their entries
        record["exp.year_start"] = min([e["start"] for e in exp if e["start"]], default=None)
        # We assume that people are always working from the beginning of their entries
        record["exp.year_start_journo"] = min(
            [e["start"] for e in exp if e["is_journo"] if e["start"]], default=None
        )
        from itertools import groupby

        blocks = [key for key, _group in groupby(e["is_journo"] for e in exp)]
        record["exp.j_blocks"] = blocks

        record["li_name_score"] = names.simpleMatchScore(
            record["full_name"], clean_name
        )
        record["n_similar"] = len(li_info["similarly_named_profiles"])
        record["li_lookup_source"] = li_lookup_src
    return record


reader = csv.DictReader(open(authors_filename), delimiter="\t")
records = []
for row in reader:
    name = row["author"]
    clean_name = name.removeprefix("and ")
    clean_name = clean_name.removeprefix("-")
    clean_name = clean_name.split(";")[0]
    clean_name = clean_name.split("/")[0]
    li_info = linkedin.get(name)
    li_redo_info = linkedin_redos.get(name)
    li_clean_supp_info = linkedin_clean_supp.get(clean_name)
    record = {"og_name": name, "og_sources": row["sources"], "clean_name": clean_name}

    record = update_li(record, li_info, clean_name, "ProxycurlLookup")
    record = update_li(record, li_redo_info, clean_name, "ProxycurlLookup")
    record = update_li(record, li_clean_supp_info, clean_name, "ProxycurlLookup")

    mr_info = muckrack.get(name)
    if mr_info:
        if "name" not in mr_info:
            record["mr_error"] = mr_info["error"]
        else:
            record["mr_name"] = mr_info["name"]
            record["mr_location"] = mr_info["location"]
            record["mr_twitter"] = mr_info["twitter"]
            record["mr_linkedin"] = mr_info["linkedin_link"]
            record["mr_website"] = mr_info["website"]
            record["detail_match"] = mr_info["detail_match"]
            record["mr_url"] = mr_info["url"]
            record["mr_name_score"] = names.simpleMatchScore(
                record["mr_name"], clean_name
            )
            li_tw_info = li_twitter.get(record["mr_twitter"])
            record = update_li(record, li_tw_info, clean_name, "ProxycurlTwitterLookup")

    records.append(record)

util.write_tsv(records, "data/author.data.tsv")
