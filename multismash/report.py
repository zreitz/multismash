from __future__ import annotations

import csv
import json
import re
from enum import Enum
from pathlib import Path


class OutputTypes(str, Enum):
    tsv = "TSV"
    gff = "GFF"


def parse_json(path: Path) -> list[dict]:
    result_list = []
    with Path.open(path, "r") as f:
        data = json.load(f)
    for record in data["records"]:
        if not record["areas"]:
            continue
        regions = [feat for feat in record["features"] if feat["type"] == "region"]
        # Add knownclusterblast if present
        try:
            knownblast = record["modules"]["antismash.modules.clusterblast"][
                "knowncluster"
            ]["results"]
        except (KeyError, TypeError, AttributeError):
            knownblast = None
        for i, region in enumerate(regions):
            # Handle origin-crossing regions with complex location
            # by taking the first and last positions
            start, *_, end = re.findall(r"\d+", region["location"])
            region_dict = {
                "file": path.stem,
                "record_id": record["name"],
                "record_length": len(record["seq"]["data"]),  # Needed for GFF
                "region": region["qualifiers"]["region_number"][0],
                "start": int(start),
                "end": int(end),
                "contig_edge": region["qualifiers"]["contig_edge"][0],
                "product": " / ".join(region["qualifiers"]["product"]),
                "record_desc": record["description"],
            }
            kcb_dict = {"KCB_hit": "", "KCB_acc": "", "KCB_sim": ""}
            if knownblast:
                hits = knownblast[i]["ranking"]
                if hits:
                    sim = hits[0][1]["similarity"]
                    if sim > 15:
                        if sim > 75:
                            sim = "high"
                        elif sim > 50:
                            sim = "medium"
                        else:
                            sim = "low"
                        kcb_dict = {
                            "KCB_hit": hits[0][0]["description"],
                            "KCB_acc": hits[0][0]["accession"],
                            "KCB_sim": sim,
                        }
            region_dict.update(kcb_dict)
            result_list.append(region_dict)
    return result_list


def write_table(regions: list[dict], outpath: str) -> None:
    fieldnames = [
        "file",
        "record_id",
        "region",
        "start",
        "end",
        "contig_edge",
        "product",
        "KCB_hit",
        "KCB_acc",
        "KCB_sim",
        "record_desc",
    ]
    with Path.open(outpath, "w") as outf:
        writer = csv.DictWriter(
            outf, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(regions)


def write_gff(regions: list[dict], outpath: str) -> None:
    """
    Write a GFF3 file according to specifications in
    https://github.com/the-sequence-ontology/specifications/blob/master/gff3.md
    The optional sequence-region pragma is not included due to laziness
    """
    rows = []
    for region in regions:
        attributes = f"ID=Region {region['region']};Product={region['product']};"

        # Handle cross-origin features
        if region["end"] < region["start"]:
            region["end"] = region["end"] + region["record_length"]

        feature = {
            "seqid": region["record_id"],
            "source": "antismash",
            "type": "region",
            "start": region["start"],
            "end": region["end"],
            "score": ".",
            "strand": ".",
            "phase": ".",
            "attributes": attributes,
        }
        rows.append(feature)

    fieldnames = [
        "seqid",
        "source",
        "type",
        "start",
        "end",
        "score",
        "strand",
        "phase",
        "attributes",
    ]
    with Path.open(outpath, "w") as outf:
        outf.write("##gff-version 3.1.26\n")
        writer = csv.DictWriter(outf, fieldnames=fieldnames, delimiter="\t")
        writer.writerows(rows)


def main(asdir: str, outpath: str, format: OutputTypes = OutputTypes.tsv):
    regions = []

    jsons = asdir.glob("*/*.json")
    for path in jsons:
        regions.extend(parse_json(path))

    # Decreasing sort priority: file, record_id, region
    regions = sorted(regions, key=lambda k: (k["file"], k["record_id"], k["region"]))

    if format == OutputTypes.tsv:
        write_table(regions, outpath)
    elif format == OutputTypes.gff:
        write_gff(regions, outpath)
    else:
        raise ValueError
