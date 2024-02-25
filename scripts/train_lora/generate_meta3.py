#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def operation(
    *,
    path_in: Path,
    path_out: Path,
) -> None:
    path_out.mkdir(exist_ok=True, parents=True)
    with path_in.open() as inf:
        d = json.load(inf)
    key2d = {}
    for k, v in d.items():
        key: str = k.split("___")[0]
        if key not in key2d:
            key2d[key] = {}
        key2d[key][k] = v

    for k, v in key2d.items():
        path_out_file = path_out.joinpath(f"{k}.json")
        with path_out_file.open("w") as outf:
            json.dump(
                v,
                outf,
                indent=4,
                ensure_ascii=False,
                sort_keys=True,
            )


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
    )


if __name__ == "__main__":
    main()
