#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

import requests


def operation(
    path_out: Path,
    special: bool,
    path_check: None | Path,
) -> bool:
    res = requests.get("https://zunko.jp/con_illust.html")
    if res.status_code != 200:
        print(res.status_code)
        raise Exception

    file_names: dict[str, str] = {}
    with path_out.open("w") as outf:
        for line in res.text.split("\n"):
            line = line.strip()
            if line.startswith("//"):
                continue
            elif line.startswith("function"):
                continue
            if "addImg" not in line:
                continue

            ext: str = ".png"
            if """'psd'""" in line or '"psd"' in line:
                ext = ".psd"
            elif "'ai'" in line or '"ai"' in line:
                ext = ".ai"

            if special:
                if ext == ".png":
                    continue
            else:
                if ext != ".png":
                    continue

            url_prefix: str = "https://zunko.jp/sozai/"
            items = line.replace("'", "").replace(");", "").replace(")", "").strip().split(",")[3:5]
            x: str = "/".join(items)
            url: str = f"{url_prefix}{x}{ext}"
            if not path_check:
                outf.write(f"{url}\n")
            file_names[Path(url).name] = url

        if path_check is not None:
            now = set()
            for f in path_check.glob("**/*"):
                now.add(f.name)
            diff = set(file_names.keys()) - now
            for d in sorted(list(diff)):
                url: str = file_names[d]
                outf.write(f"NEW\t{d}\t{url}\n")
            if len(diff) > 0:
                return False
    return True


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--special", action="store_true")
    oparser.add_argument("--check", type=Path)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    ok = operation(
        opts.output,
        opts.special,
        opts.check,
    )
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
