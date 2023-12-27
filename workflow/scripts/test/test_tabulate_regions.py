import unittest
from multismash.workflow.scripts.tabulate_regions import *

import json
from pathlib import Path

with open("workflow/scripts/test/fake_antismash/GCF_000407825_parsed.json") as inf:
    parsed_good = json.load(inf)

class TestTabulate(unittest.TestCase):
    def test_parse(self):
        path = "workflow/scripts/test/fake_antismash/GCF_000407825_minimal.json"
        parsed = parse_json(Path(path))
        assert(parsed == parsed_good)

