# Mostly written by ChatGPT
from __future__ import annotations

import unittest
from pathlib import Path

from ..multismash.count_regions import build_table, main, parse_json

unittest.util._MAX_LENGTH = 2000


def test_parse_json_has():
    path = Path(__file__).parent / "data" / "antismash" / "has" / "has.json"
    (fname, by_contig, descs) = parse_json(path)

    assert fname == "GCF_000407825_adjusted"
    assert by_contig == {
        "NZ_KE136672": [["thiopeptide"], ["arylpolyene"]],
        "NZ_KE136673": [],
        "NZ_KE136674": [["RiPP-like"]],
        "NZ_KE136675": [
            ["NRP-metallophore", "NRPS", "T1PKS"],
            ["NRP-metallophore", "NRPS"],
        ],
    }
    assert descs == {
        "NZ_KE136672": "NZ_KE136672",
        "NZ_KE136673": "NZ_KE136673",
        "NZ_KE136674": "NZ_KE136674",
        "NZ_KE136675": "NZ_KE136675",
    }


def test_parse_json_hasnt():
    path = Path(__file__).parent / "data" / "antismash" / "hasnt" / "hasnt.json"
    (fname, by_contig, descs) = parse_json(path)

    assert fname == "GCF_nothing"
    assert by_contig == {"NZ_nothing": []}
    assert descs == {"NZ_nothing": "no BGCs"}


by_genome = {
    "genome1": {
        "NZ_KE136672": [["thiopeptide"], ["arylpolyene"]],
        "NZ_KE136673": [],
        "NZ_KE136674": [["RiPP-like"]],
        "NZ_KE136675": [
            ["NRP-metallophore", "NRPS", "T1PKS"],
            ["NRP-metallophore", "NRPS"],
        ],
    },
    "genome2": {"NZ_nothing": []},
}
descriptions = {
    "genome1": {
        "NZ_KE136672": "NZ_KE136672",
        "NZ_KE136673": "NZ_KE136673",
        "NZ_KE136674": "NZ_KE136674",
        "NZ_KE136675": "NZ_KE136675",
    },
    "genome2": {"NZ_nothing": "no BGCs"},
}


def test_build_table_default():
    result = build_table(by_genome, descriptions, False, False)
    assert result == [
        {
            "thiopeptide": 1,
            "arylpolyene": 1,
            "RiPP-like": 1,
            "hybrid": 2,
            "record": "genome1",
            "total_count": 5,
            "description": "NZ_KE136672 [4 total records]",
        },
        {
            "record": "genome2",
            "total_count": 0,
            "description": "no BGCs [1 total record]",
        },
    ]


def test_build_table_by_contig():
    result = build_table(by_genome, descriptions, True, False)
    assert result == [
        {
            "thiopeptide": 1,
            "arylpolyene": 1,
            "record": "genome1|NZ_KE136672",
            "total_count": 2,
            "description": "NZ_KE136672",
        },
        {
            "record": "genome1|NZ_KE136673",
            "total_count": 0,
            "description": "NZ_KE136673",
        },
        {
            "RiPP-like": 1,
            "record": "genome1|NZ_KE136674",
            "total_count": 1,
            "description": "NZ_KE136674",
        },
        {
            "hybrid": 2,
            "record": "genome1|NZ_KE136675",
            "total_count": 2,
            "description": "NZ_KE136675",
        },
        {"record": "genome2|NZ_nothing", "total_count": 0, "description": "no BGCs"},
    ]


def test_build_table_split():
    result = build_table(by_genome, descriptions, False, True)
    assert result == [
        {
            "thiopeptide": 1,
            "arylpolyene": 1,
            "RiPP-like": 1,
            "NRP-metallophore": 2,
            "NRPS": 2,
            "T1PKS": 1,
            "record": "genome1",
            "total_count": 5,
            "description": "NZ_KE136672 [4 total records]",
        },
        {
            "record": "genome2",
            "total_count": 0,
            "description": "no BGCs [1 total record]",
        },
    ]


def test_build_table_both():
    result = build_table(by_genome, descriptions, True, True)
    assert result == [
        {
            "thiopeptide": 1,
            "arylpolyene": 1,
            "record": "genome1|NZ_KE136672",
            "total_count": 2,
            "description": "NZ_KE136672",
        },
        {
            "record": "genome1|NZ_KE136673",
            "total_count": 0,
            "description": "NZ_KE136673",
        },
        {
            "RiPP-like": 1,
            "record": "genome1|NZ_KE136674",
            "total_count": 1,
            "description": "NZ_KE136674",
        },
        {
            "NRP-metallophore": 2,
            "NRPS": 2,
            "T1PKS": 1,
            "record": "genome1|NZ_KE136675",
            "total_count": 2,
            "description": "NZ_KE136675",
        },
        {"record": "genome2|NZ_nothing", "total_count": 0, "description": "no BGCs"},
    ]


def test_main(tmp_path):
    gold = (Path(__file__).parent / "data" / "gold_count.tsv").read_text()

    inpath = Path(__file__).parent / "data" / "antismash"
    outpath = tmp_path / "test_count.tsv"

    main(inpath, outpath)

    assert outpath.read_text() == gold
