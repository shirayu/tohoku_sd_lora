#!/usr/bin/env python3

import argparse
import shutil
from pathlib import Path

from prepare_for_kohya_ss_sd_scripts import name2prompt


def operation(
    *,
    path_in: Path,
    path_out: Path,
    prefix: str,
) -> None:
    path_out.mkdir(exist_ok=True, parents=True)
    for dirpath in path_in.iterdir():
        target = dirpath.joinpath("last.safetensors")
        if not target.exists():
            continue
        name = {
            "zunko_oc__withchara": "ZunkoOC",
            "kiritan_oc__withchara.mod": "KiritanOC",
            "itako_oc__withchara.mod": "ItakoOC",
        }.get(dirpath.name)
        if name is None:
            name = name2prompt(name=dirpath.name.replace(".mod", ""), nosd=True)
        assert name is not None
        topath = path_out.joinpath(prefix + name + target.suffix)
        print(f"{target} -> {topath}")
        shutil.copy(target, topath)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--prefix")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        prefix=opts.prefix,
    )


if __name__ == "__main__":
    main()
