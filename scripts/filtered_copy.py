#!/usr/bin/env python3

import argparse
import shutil
from collections import defaultdict
from pathlib import Path


def operation(
    *,
    path_in: Path,
    path_out: Path,
    path_ex: Path,
) -> None:
    parent2name = defaultdict(set)

    # Get exclude file names
    with path_ex.open() as inf:
        for line in inf:
            items = line[:-1].split("\t")
            assert len(items) == 2
            parent2name[items[0]].add(items[1])

    for path_dir in path_in.iterdir():
        if not path_dir.is_dir():
            continue
        if path_in.joinpath(f"{path_dir.name}.mod").exists():
            continue

        for p in path_dir.iterdir():
            parent: str = p.parent.name
            name: str = p.name

            if name in parent2name.get(parent, {}):
                continue

            if parent == "zundamon_sd":
                parent = "zundamon"

            op = path_out.joinpath(parent)
            op.mkdir(parents=True, exist_ok=True)
            shutil.copy(p, op)

            if "_oc" in parent:
                another_parent: str = parent.replace("_oc", "_oc__withchara")
                op2 = path_out.joinpath(another_parent)
                op2.mkdir(parents=True, exist_ok=True)
                shutil.copy(p, op2)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--exclude", "--ex", type=Path, required=True)

    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        path_ex=opts.exclude,
    )


if __name__ == "__main__":
    main()
