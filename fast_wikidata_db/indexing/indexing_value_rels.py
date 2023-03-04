"""
Create json files containing:
{QID: {PID: [List of values]}}
filename: QID % NUM_FILES
"""
import os
import json
import argparse
from tqdm import tqdm
from typing import Dict, List
from os.path import exists, join
from collections import defaultdict
from fast_wikidata_db.indexing.utils import get_file_index


def jsonl_to_json(jsonl_dir: str):
    data_dict: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    with open(jsonl_dir, "r") as f:
        for line in f:
            data_dict = json.loads(line)
            for qcode, value_rel in data_dict.items():
                for pcode, value in value_rel.items():
                    data_dict[qcode][pcode].extend(value)
    with open(jsonl_dir.replace(".jsonl", ".json"), "w") as f:
        f.write(json.dumps(data_dict))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True, help="path to preprocessed dump of value_rels")
    parser.add_argument("--output_dir", type=str, required=True, help="path to output directory")
    parser.add_argument("--num_files", type=int, default=10000)
    args = parser.parse_args()

    output_dir = join(args.output_dir, "value_rels")
    if not exists(output_dir):
        os.makedirs(output_dir)

    input_files = [join(args.input_dir, f) for f in os.listdir(args.input_dir) if f.endswith(".jsonl")]
    for input_file in tqdm(input_files):
        with open(input_file) as f:
            for line in f:
                data_dict = json.loads(line)
                qcode, pcode, value = data_dict["qid"], data_dict["property_id"], data_dict["value"]

                data_dict = {qcode: {pcode: [value]}}

                data_index = get_file_index(qcode, args.num_files)
                with open(join(output_dir, str(data_index) + ".jsonl"), "a") as save_file:
                    save_file.write(f"{json.dumps(data_dict)}\n")

    # Merge multiple dictionaries in jsonl into one dictionary
    # value_rels
    for file_name in os.listdir(output_dir):
        if file_name.endswith(".jsonl"):
            jsonl_to_json(join(output_dir, file_name))

    # Remove jsonl files
    for file_name in os.listdir(output_dir):
        if file_name.endswith(".jsonl"):
            os.remove(join(output_dir, file_name))


if __name__ == "__main__":
    main()