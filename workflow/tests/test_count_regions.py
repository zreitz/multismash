from scripts.count_regions import *

parsed0 = ("has0",
           {"contig1": [],
            "contig2": []})
parsed3 = ("has3",
           {"contig1": [["NRPS", "PKS"], ["NRPS"], ["PKS"]]})
parsed4 = ("has4",
           {"contig1": [["terpene"], ["terpene"]],
            "contig2": [["terpene"], ["terpene"]]})

type_dict = {k: v for k, v in (parsed0, parsed3, parsed4)}


def test_parse0():
    path = "workflow/tests/fake_antismash/has0/has0.json"
    parsed = parse_json(path)
    assert(parsed == parsed0)


def test_parse3():
    path = "workflow/tests/fake_antismash/has3/has3.json"
    parsed = parse_json(path)
    assert(parsed == parsed3)


def test_parse4():
    path = "workflow/tests/fake_antismash/has4/has4.json"
    parsed = parse_json(path)
    assert(parsed == parsed4)


def test_tabulate_default():
    lst = tabulate(type_dict)
    good = [
        {"record": "has0", "total_count": 0},
        {"record": "has3", "total_count": 3, 'NRPS': 2, 'PKS': 2},
        {"record": "has4", "total_count": 4, 'terpene': 4}
    ]
    assert(lst == good)


def test_tabulate_contig():
    lst = tabulate(type_dict, contig=True)
    good = [
        {"record": "has0|contig1", "total_count": 0},
        {"record": "has0|contig2", "total_count": 0},
        {"record": "has3|contig1", "total_count": 3, 'NRPS': 2, 'PKS': 2},
        {"record": "has4|contig1", "total_count": 2, 'terpene': 2},
        {"record": "has4|contig2", "total_count": 2, 'terpene': 2}
    ]
    assert(lst == good)


def test_tabulate_hybrid():
    lst = tabulate(type_dict, hybrid=True)
    good = [
        {"record": "has0", "total_count": 0},
        {"record": "has3", "total_count": 3, 'NRPS': 1, 'PKS': 1, 'hybrid': 1},
        {"record": "has4", "total_count": 4, 'terpene': 4}
    ]
    assert(lst == good)
