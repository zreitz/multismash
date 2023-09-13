## Given a bunch of antismash results, count the BGC regions
## Usage:
##      python count_regions.py -h

import csv
from pathlib import Path
import json
import argparse


def parse_json(path):
    by_contig = {}
    with open(str(path), 'r') as f:
        data = json.load(f)
    for record in data["records"]:
        products = [a["products"] for a in record["areas"]]
        by_contig[record["name"]] = products
    return data["input_file"], by_contig


def tabulate(type_dict, contig=False, split_hybrids=False):
    table_list = []
    this_row = {}
    for genome, g_prods in type_dict.items():
        for cont, regions in g_prods.items():
            for region in regions:
                if len(region) > 1 and not split_hybrids:
                    this_row["hybrid"] = this_row.get("hybrid", 0) + 1
                    continue
                for prod in region:
                    this_row[prod] = this_row.get(prod, 0) + 1
            if contig:
                this_row["record"] = "|".join((genome, cont))
                this_row["total_count"] = len(regions)
                table_list.append(this_row)
                this_row = {}
        if not contig:
            this_row["record"] = genome
            this_row["total_count"] = sum((len(regions) for regions in g_prods.values()))
            table_list.append(this_row)
            this_row = {}
    return table_list


def main(asdir: str, outpath: str, contig: bool = False, hybrid: bool = False):
    by_genome = {}

    jsons = Path(asdir).glob("*/*.json")
    for path in jsons:
        genome, types = parse_json(path)
        by_genome[genome] = types

    table_list = tabulate(by_genome, contig, hybrid)
    all_products = set().union(*(d.keys() for d in table_list))
    all_products.difference_update({"record", "total_count"})
    fieldnames = ["record", "total_count"] + sorted(all_products)

    with open(outpath, 'w') as outf:
        writer = csv.DictWriter(outf, fieldnames=fieldnames,
                                delimiter='\t', restval=0)
        writer.writeheader()
        writer.writerows(table_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given a bunch of antismash results, count the BGC regions")

    parser.add_argument("asdir", type=str,
                        help="directory containing antiSMASH directories")
    parser.add_argument("outpath", type=str,
                        help="desired path+name for the output TSV")
    parser.add_argument("--by_contig", action="store_true",
                        help="count regions per each individual contig rather than per assembly")
    parser.add_argument("--split_hybrids", action="store_true",
                        help="count each hybrid region multiple times, once for each "
                             "constituent BGC class. Caution: this flag artificially "
                             "inflates total BGC counts")

    args = parser.parse_args()

    main(args.asdir, args.outpath, args.by_contig, args.split_hybrids)
