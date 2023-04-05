#!/usr/bin/env python3

import argparse
import time
from pathlib import Path

import requests


def operation(path_in: Path, path_out: Path) -> None:
    assert path_in.is_dir()

    path_out.mkdir(exist_ok=True, parents=True)

    for lf in path_in.iterdir():
        if lf.name.startswith("_"):
            continue

        grp: str = lf.name.split(".")[0]
        path_myout: Path = path_out.joinpath(grp)
        path_myout.mkdir(exist_ok=True, parents=True)
        with lf.open() as inf:
            for line in inf:
                if len(line.strip()) == 0 or line.startswith("#"):
                    continue

                url: str = line[:-1]
                outname: str = url.split("/")[-1]
                op: Path = path_myout.joinpath(outname)
                if op.exists():
                    print(f"{url} -> {op} (SKIP)")
                    continue
                print(f"{url} -> {op}")

                r = requests.get(url)
                with op.open("wb") as ob:
                    ob.write(r.content)
                time.sleep(5)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
    )
    oparser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
    )
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.input, opts.output)


if __name__ == "__main__":
    main()
