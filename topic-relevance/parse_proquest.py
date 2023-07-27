from data_wrangler import proquest
import argparse
import os

# Convert proquest data to txtfiles that we can parse 

def get_files_in_dir(dirname):
    for filename in os.listdir(dirname):
        if filename.endswith(".xml"):
            yield os.path.join(dirname, filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="proquest parser"
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to the proquest directory"
    )
    args = parser.parse_args()
    records = []
    if os.path.isdir(args.path):
        os.chdir(args.path)
        files = get_files_in_dir('raw')
        for file in files:
            print('parsing' + file)
            records.append(proquest.parse_proquest_xml(file))
    proquest.save_txtfiles(records, 'txt')
