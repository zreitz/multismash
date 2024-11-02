# Mostly written by ChatGPT
from __future__ import annotations

import json
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import mock_open, patch

from ..tabulate_regions import parse_json


class TestParseJson(unittest.TestCase):
    def setUp(self):
        # Sample JSON data that mimics antiSMASH results
        self.sample_json = {
            "records": [
                {
                    "name": "record1",
                    "description": "Sample description",
                    "areas": [1],
                    "features": [
                        {
                            "type": "region",
                            "location": "100..500",
                            "qualifiers": {
                                "region_number": ["1"],
                                "contig_edge": ["True"],
                                "product": ["Polyketide"],
                            },
                        }
                    ],
                    "modules": {
                        "antismash.modules.clusterblast": {
                            "knowncluster": {
                                "results": [
                                    {
                                        "ranking": [
                                            [
                                                {
                                                    "description": "similar cluster",
                                                    "accession": "ABC123",
                                                },
                                                {"similarity": 80},
                                            ]
                                        ]
                                    }
                                ]
                            }
                        }
                    },
                }
            ]
        }
        self.expected_output = [
            {
                "file": "sample",
                "record_id": "record1",
                "region": "1",
                "start": "100",
                "end": "500",
                "contig_edge": "True",
                "product": "Polyketide",
                "record_desc": "Sample description",
                "KCB_hit": "similar cluster",
                "KCB_acc": "ABC123",
                "KCB_sim": "high",
            }
        ]

    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_parse_json_with_knownclusterblast(self, mock_open):
        # Mock the file content and path
        mock_open.return_value = StringIO(json.dumps(self.sample_json))
        path = Path("sample.json")

        # Call parse_json and check the result
        result = parse_json(path)
        assert result == self.expected_output

    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_parse_json_no_knownclusterblast(self, mock_open):
        # Remove knownclusterblast section from sample JSON
        self.sample_json["records"][0]["modules"] = {}
        self.expected_output[0].update({"KCB_hit": "", "KCB_acc": "", "KCB_sim": ""})

        # Mock the file content and path
        mock_open.return_value = StringIO(json.dumps(self.sample_json))
        path = Path("sample.json")

        # Call parse_json and check the result
        result = parse_json(path)
        assert result == self.expected_output

    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_parse_json_no_areas(self, mock_open):
        # Set areas to an empty list to test area filtering
        self.sample_json["records"][0]["areas"] = []

        # Mock the file content and path
        mock_open.return_value = StringIO(json.dumps(self.sample_json))
        path = Path("sample.json")

        # Call parse_json and check the result is empty due to no areas
        result = parse_json(path)
        assert result == []

    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_parse_json_no_region_features(self, mock_open):
        # Set features to an empty list to simulate no regions
        self.sample_json["records"][0]["features"] = []

        # Mock the file content and path
        mock_open.return_value = StringIO(json.dumps(self.sample_json))
        path = Path("sample.json")

        # Call parse_json and check the result is empty due to no region features
        result = parse_json(path)
        assert result == []


if __name__ == "__main__":
    unittest.main()
