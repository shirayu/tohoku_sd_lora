#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def operation(
    *,
    path_in: Path,
    path_out: Path,
    key: str,
) -> None:
    with path_in.open() as inf, path_out.open("w") as outf:
        key2triggerinfo = json.load(inf)
        trigger_info: dict[str, str] = {}
        if key == "oistyle":
            trigger_info = {
                "train": key,
                "generate": key,
            }
        else:
            trigger_info = key2triggerinfo[key]

        info: dict = {
            "trigger_info": trigger_info,
        }
        outf.write(json.dumps(info, indent=4))
        outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--key", required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        key=opts.key,
    )


if __name__ == "__main__":
    main()
