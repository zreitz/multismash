## Given a bunch of antismash results, tabulate BGC regions
## Usage:
##      python tabulate_regions.py -h

import csv
from pathlib import Path
import re
import json
import argparse


def parse_json(path):
    result_list = []
    with open(str(path), 'r') as f:
        data = json.load(f)
    for record in data["records"]:
        if not record["areas"]:
            continue
        regions = [feat for feat in record["features"]
                   if feat["type"] == "region"]
        # Add knownclusterblast if present
        try:
            knownblast = record["modules"]["antismash.modules.clusterblast"]["knowncluster"]["results"]
        except (KeyError, TypeError, AttributeError):
            knownblast = None
        for i, region in enumerate(regions):
            start, end = re.findall(r'\d+', region["location"])
            region_dict = {
                "file":         path.stem,
                "record_id":    record["name"],
                "region":       region["qualifiers"]["region_number"][0],
                "start":        start,
                "end":          end,
                "contig_edge":  region["qualifiers"]["contig_edge"][0],
                "product":      " / ".join(region["qualifiers"]["product"]),
                "record_desc":  record["description"]
            }
            kcb_dict = {"KCB_hit": "", "KCB_acc": "", "KCB_sim": ""}
            if knownblast:
                hits = knownblast[i]["ranking"]
                if hits:
                    sim = hits[0][1]["similarity"]
                    if sim > 15:
                        if sim > 75: sim = "high"
                        elif sim > 50: sim = "medium"
                        else: sim = "low"
                        kcb_dict = {
                            "KCB_hit": hits[0][0]["description"],
                            "KCB_acc": hits[0][0]["accession"],
                            "KCB_sim": sim
                        }
            region_dict.update(kcb_dict)
            result_list.append(region_dict)
    return result_list


def main(asdir, outpath):
    record_infos = []

    jsons = Path(asdir).glob("*/*.json")
    for path in jsons:
        record_infos.extend(parse_json(path))

    fieldnames = ["file", "record_id", "region",
                  "start", "end", "contig_edge",
                  "product",
                  "KCB_hit", "KCB_acc", "KCB_sim",
                  "record_desc"]
    with open(outpath, 'w') as outf:
        writer = csv.DictWriter(outf, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(record_infos)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given a bunch of antismash results, tabulate BGC regions")

    parser.add_argument("asdir", type=str,
                        help="directory containing antiSMASH directories")
    parser.add_argument("outpath", type=str,
                        help="desired path+name for the output TSV")

    args = parser.parse_args()

    main(args.asdir, args.outpath)
