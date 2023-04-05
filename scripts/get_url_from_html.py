#!/usr/bin/env python3

import argparse
from pathlib import Path


def operation(path_in: Path, path_out: Path) -> None:
    with path_in.open() as inf, path_out.open("w") as outf:
        for line in inf:
            if "addImg" not in line:
                continue

            ext: str = ".png"
            if """'psd'""" in line or '"psd"' in line:
                ext = ".psd"
            elif "'ai'" in line or '"ai"' in line:
                ext = ".ai"
            url_prefix: str = "https://zunko.jp/sozai/"
            items = line.replace("'", "").replace(")", "").replace(");", "").strip().split(",")[3:5]
            x: str = "/".join(items)
            url: str = f"{url_prefix}{x}{ext}"
            outf.write(f"{url}\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.input, opts.output)


if __name__ == "__main__":
    main()
