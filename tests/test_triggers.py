#!/usr/bin/env python3

import json
from pathlib import Path


def test_options():
    with Path("./data/trigger.json").open() as inf:
        d = json.load(inf)
    ALL_TRIGGERS = sorted(list(d.keys()))
    print(f"ALL_TRIGGERS: {len(ALL_TRIGGERS)}")
    print(f"\t{ALL_TRIGGERS}")

    # Check each URL file name is one of  trigger words
    for tgt in [
        "./data/urls/",
        "./data/img/original",
        "./data/img/converted",
        "./data/img/train_1024",
    ]:
        t: Path = Path(tgt)
        if not t.exists():
            continue
        for f in t.iterdir():
            if f.name.startswith("_"):
                continue

            name: str = f.stem.replace("_sd", "")
            assert name in ALL_TRIGGERS
