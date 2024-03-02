#!/usr/bin/env python3

import json
from pathlib import Path


def test_options():
    with Path("./data/tag_target.json").open() as inf:
        d = json.load(inf)
    ALL_TRIGGERS = sorted(list(d.keys()))
    print(f"ALL_TRIGGERS: {len(ALL_TRIGGERS)}")
    print(f"\t{ALL_TRIGGERS}")

    for f in Path("./data/urls/").iterdir():
        if f.is_dir():
            continue

        assert f.stem in ALL_TRIGGERS
