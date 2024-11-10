from __future__ import annotations

import json
import unittest
from pathlib import Path

from ..multismash.overview import main, parse_json

unittest.util._MAX_LENGTH = 2000


def test_parse_json_has():
    path = Path(__file__).parent / "data" / "antismash" / "has" / "has.json"
    result = parse_json(path)

    path = Path(__file__).parent / "data" / "gold_parsed.json"
    with Path.open(path) as f:
        expected = json.load(f)

    assert result == expected


def test_parse_json_hasnt():
    path = Path(__file__).parent / "data" / "antismash" / "hasnt" / "hasnt.json"
    result = parse_json(path)

    expected = []

    assert result == expected


def test_parse_json(tmp_path):
    gold = (Path(__file__).parent / "data" / "gold_tabulate.tsv").read_text()

    inpath = Path(__file__).parent / "data" / "antismash"
    outpath = tmp_path / "test_tabulate.tsv"

    main(inpath, outpath)

    assert outpath.read_text() == gold
