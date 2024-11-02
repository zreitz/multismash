# Mostly written by ChatGPT
from __future__ import annotations

import json
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import mock_open, patch

from ..count_regions import parse_json, tabulate

unittest.util._MAX_LENGTH = 2000


class TestCountRegions(unittest.TestCase):
    def setUp(self):
        # Sample JSON data to mimic antiSMASH results for `parse_json`
        self.sample_json = {
            "input_file": "genome1",
            "records": [
                {
                    "name": "contig1",
                    "description": "Test description 1",
                    "areas": [
                        {"products": ["Type I PKS"]},
                        {"products": ["NRPS", "Type II PKS"]},
                    ],
                },
                {
                    "name": "contig2",
                    "description": "Test description 2",
                    "areas": [{"products": ["Terpene"]}, {"products": ["Type I PKS"]}],
                },
            ],
        }
        self.expected_parse_json_output = (
            "genome1",
            {
                "contig1": [["Type I PKS"], ["NRPS", "Type II PKS"]],
                "contig2": [["Terpene"], ["Type I PKS"]],
            },
            {"contig1": "Test description 1", "contig2": "Test description 2"},
        )

    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_parse_json(self, mock_open):
        # Mock file content and path
        mock_open.return_value = StringIO(json.dumps(self.sample_json))
        path = Path("genome1.json")

        # Test parse_json function
        result = parse_json(path)
        assert result == self.expected_parse_json_output

    def test_tabulate_contig_false(self):
        # Data for `tabulate` function with `contig=False`
        type_dict = {
            "genome1": {
                "contig1": [["Type I PKS"], ["NRPS", "Type II PKS"]],
                "contig2": [["Terpene"], ["Type I PKS"]],
            }
        }
        descriptions = {
            "genome1": {
                "contig1": "Test description 1",
                "contig2": "Test description 2",
            }
        }
        expected_output = [
            {
                "record": "genome1",
                "hybrid": 1,
                "Type I PKS": 2,
                "Terpene": 1,
                "total_count": 4,
                "description": "Test description 1 [2 total records]",
            }
        ]

        # Test tabulate function with contig=False
        result = tabulate(type_dict, descriptions, contig=False, split_hybrids=False)
        assert result == expected_output

    def test_tabulate_contig_true(self):
        # Data for `tabulate` function with `contig=True`
        type_dict = {
            "genome1": {
                "contig1": [["Type I PKS"], ["NRPS", "Type II PKS"]],
                "contig2": [["Terpene"], ["Type I PKS"]],
            }
        }
        descriptions = {
            "genome1": {
                "contig1": "Test description 1",
                "contig2": "Test description 2",
            }
        }
        expected_output = [
            {
                "record": "genome1|contig1",
                "Type I PKS": 1,
                "hybrid": 1,
                "total_count": 2,
                "description": "Test description 1",
            },
            {
                "record": "genome1|contig2",
                "Type I PKS": 1,
                "Terpene": 1,
                "total_count": 2,
                "description": "Test description 2",
            },
        ]

        # Test tabulate function with contig=True
        result = tabulate(type_dict, descriptions, contig=True, split_hybrids=False)
        assert result == expected_output

    def test_tabulate_split_hybrids(self):
        # Data for `tabulate` function with `split_hybrids=True`
        type_dict = {
            "genome1": {
                "contig1": [["Type I PKS"], ["NRPS", "Type II PKS"]],
                "contig2": [["Terpene"], ["Type I PKS"]],
            }
        }
        descriptions = {
            "genome1": {
                "contig1": "Test description 1",
                "contig2": "Test description 2",
            }
        }
        expected_output = [
            {
                "record": "genome1",
                "Type I PKS": 2,
                "NRPS": 1,
                "Type II PKS": 1,
                "Terpene": 1,
                "total_count": 4,
                "description": "Test description 1 [2 total records]",
            }
        ]

        # Test tabulate function with split_hybrids=True
        result = tabulate(type_dict, descriptions, contig=False, split_hybrids=True)
        assert result == expected_output


if __name__ == "__main__":
    unittest.main()
