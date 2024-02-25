#!/usr/bin/env python3

import argparse
import shutil
from pathlib import Path


def operation(
    *,
    path_in: Path,
    path_out: Path,
) -> None:
    path_out.mkdir(exist_ok=True, parents=True)
    for f in path_in.glob("**/mymodel.safetensors"):
        new_name: str = f.parent.name + ".safetensors"
        new_name = new_name.replace(".mod", "")
        myout = path_out.joinpath(new_name)
        x: int = 2
        while True:
            if not myout.exists():
                break
            myout = path_out.joinpath(f.parent.name + f".v{x}.safetensors")
            x += 1
        shutil.copy(f, myout)
        print(f"{f} -> {myout}")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
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
