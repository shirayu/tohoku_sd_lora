#!/usr/bin/env python3

import argparse
from pathlib import Path


def operation(
    *,
    path_in: Path,
) -> None:
    checked_dir: set[Path] = set()
    for f in path_in.glob("**/*.png"):
        if f.parent.name != "sample":
            continue

        tmp = f.stem.split("_")
        if len(tmp) < 5:
            print(f"Skip: {f}")
            continue

        # <name>_<time>_<step>_<num>_<seed>.png
        prompt_id: str = tmp[-2]
        new_dir: Path = f.parent.joinpath(prompt_id)

        if new_dir not in checked_dir:
            new_dir.mkdir(exist_ok=True, parents=True)
            checked_dir.add(new_dir)

        step: str = tmp[-3]
        if step == "e000000":
            step = "000000"
        new_name = new_dir.joinpath("_".join([prompt_id, step]) + f.suffix)
        print(f, "\n ->", new_name)
        f.rename(new_name)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
    )


if __name__ == "__main__":
    main()
