from squidtools import util
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("fine_tuned_org_match_model.bert")

def apply_hf(infile, outfile, org_key="organization", dime_key="name"):
    records = util.read_delim(infile)

    orgs = [r[org_key] for r in records]
    dime = [r[dime_key] for r in records]
    org_embeddings = model.encode(orgs)
    dime_embeddings = model.encode(dime)
    sims = [
        float(model.similarity(o, d)) for o, d in zip(org_embeddings, dime_embeddings)
    ]
    for r, s in zip(records, sims):
        r["sim"] = s
    util.write_tsv(records, outfile)

apply_hf(
    "maybes.ts.stg0.tsv",
    "maybes.ts.stg0.bert.tsv",
)
