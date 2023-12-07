import argparse
import statistics
import csv
import os
import json

"""
Input: JSON source of article sources, including a filename key
Outputs a Potato json task for every article with sources correctly embedded
"""

style = "font-size:12pt;font-weight:400;"

def process_sources(sources):
    html = "<div id='source_options'>"
   
    for source in sources:
        name = source['person_name']
        title = source.get('person_title')
        org = source.get('organization')
        doc = source.get('document')
        category = source['category']
        html += f"<p>{name}|{title}|{org}|{doc}|{category}</p>"
    html += "</div>"
    return html


def process_paragraph(text):
    result = f"<p style='{style}'>{text}</p>"
    return result


def make_text(text, sources):
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    wrapped_paragraphs = [process_paragraph(p) for p in paragraphs]
    text = ''.join(wrapped_paragraphs)
    sources = process_sources(sources)
    return f"{sources}<div>{text}</div>"

def process_article(row, data_dir, filename_column='filename', source_column='sources'):
    filename = row.get(filename_column)
    abspath = f"{data_dir}/" + filename
    sources = row[source_column]
    if isinstance(sources, dict) and len(sources.keys()) == 1:
        sources = sources[list(sources.keys())[0]]
    if filename:
        with open(abspath, 'r', encoding='utf-8') as text_file:
            content = text_file.read()
            text = make_text(content, sources)
            return {
                "id": filename, 
                "text": text,
                'n_sources': len(sources)
            }


def process_json(jsonfile):
    records = []
    with open(jsonfile, 'rt') as file:
        for line in file:
            article = json.loads(line)
            potato_record = process_article(article, data_dir=os.path.dirname(jsonfile))
            records.append(potato_record)
    return records

def main():
    parser = argparse.ArgumentParser(description='Convert tsv to JSON for potato')
    parser.add_argument('file', help='JOSN file containing a column with filenames and sources')
    parser.add_argument('json_file', help='Destination JSON file')
    args = parser.parse_args()
    records = process_json(args.file)
    with open(args.json_file, 'wt') as of: 
        for r in records:
            if (r['n_sources'] < 15 and r['n_sources'] > 0):
                of.write(json.dumps(r))
                of.write('\n')
            else: 
                print(f"excluded source with {r['n_sources']} sources")
    ns = [r['n_sources'] for r in records]
    print(statistics.mean(ns))
    print(statistics.stdev(ns))
    print(max(ns))


if __name__ == "__main__":
    main()
