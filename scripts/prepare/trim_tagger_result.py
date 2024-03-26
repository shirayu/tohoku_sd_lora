#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def operation(
    *,
    path_in: Path,
    path_out: Path,
) -> None:
    with path_in.open() as inf, path_out.open("w") as outf:
        for line in inf:
            d = json.loads(
                line,
                parse_float=lambda x: round(float(x), 3),
            )
            ifp = Path(d["input"])
            d["input"] = str(Path(ifp.parent.name).joinpath(Path(d["input"]).name))
            outf.write(json.dumps(d, ensure_ascii=False, sort_keys=True))
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
