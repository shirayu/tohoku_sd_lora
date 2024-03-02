#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

ALL_KEYS: set[str] = {
    "Anko",
    "Awamo",
    "Chanko",
    "Chuwa",
    "Hokamel",
    "Itako",
    "Itoc",
    "Kioc",
    "Kiritan",
    "Metan",
    "Shinobi",
    "Sora",
    "Tsurugi",
    "Usagi",
    "Zfr",
    "Zundamon",
    "Zunko",
    "Zuoc",
}


def operation(
    *,
    path_in: Path,
    path_out: Path,
) -> None:
    with path_in.open() as inf, path_out.open("w") as outf:
        d = json.load(inf)
        pr: str = list(d.values())[0]["caption"]
        key: str = pr.split(", |||")[0]
        assert key in ALL_KEYS

        trigger: str = key
        if trigger in {"Itoc", "Kioc", "Zuoc"}:
            trigger = f"1girl wear {key}"

        info: dict[str, str] = {
            "trigger": trigger,
        }
        outf.write(json.dumps(info, indent=4))
        outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
    )


if __name__ == "__main__":
    main()
