#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


def operation(
    *,
    path_in: Path,
    path_out: Path,
) -> None:
    with path_in.open() as inf, path_out.open("w") as outf:
        ds = json.load(inf)

        new_ds = {}
        for k, v in ds.items():
            if "train_resolution" not in v:
                sys.stderr.write(f"Exclude\t{k}\n")
                continue
            new_ds[k] = v
        outf.write(json.dumps(new_ds, indent=4))
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
