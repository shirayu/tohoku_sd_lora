#!/usr/bin/env python3

import argparse
from collections import defaultdict
from pathlib import Path


def operation(
    *,
    path_in: Path,
    path_out: Path,
    path_ex: Path,
    for_style: bool,
) -> None:
    path_out.mkdir(exist_ok=True, parents=True)
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

            if for_style and (parent.endswith("_sd") or parent.endswith("oc") or "Zfr" in parent or "Chuwa" in parent):
                continue

            if name in parent2name.get(parent, {}):
                continue

            path_out.joinpath(f"{parent}___{p.name}").symlink_to(p.absolute())

            if parent.endswith("oc"):
                another_parent: str = parent[:-2] + "oc__withchara"
                path_out.joinpath(f"{another_parent}___{p.name}").symlink_to(p.absolute())


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--exclude", "--ex", type=Path, required=True)
    oparser.add_argument("--for_style", action="store_true")

    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        path_ex=opts.exclude,
        for_style=opts.for_style,
    )


if __name__ == "__main__":
    main()
