#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def operation(
    *,
    path_in: Path,
    path_out: Path,
    path_positive_prompt: Path | None,
    path_negative_prompt: Path | None,
    scale: float = 7.0,
    step: int = 30,
    seed: int = 1234,
    path_config: Path,
) -> None:
    with path_config.open() as inf:
        config = json.load(inf)
        trigger: str = config["trigger_info"]["generate"]

    common_positive: str = ""
    if path_positive_prompt is not None:
        with path_positive_prompt.open() as inf:
            common_positive = inf.read().replace("\n", " ")

    common_negative: str = ""
    if path_negative_prompt is not None:
        with path_negative_prompt.open() as inf:
            common_negative = inf.read().replace("\n", " ")

    with path_in.open() as inf, path_out.open("w") as outf:
        for line in inf:
            line = line.strip().replace("<trigger>", trigger).replace("<positive_quality>", common_positive)

            if line.startswith("#") or len(line) == 0:
                continue

            if " --d " not in line:
                line += f" --d {seed}"
            if " --l " not in line:
                line += f" --l {scale}"
            if " --s " not in line:
                line += f" --s {step}"
            if " --n " not in line:
                line += f" --n {common_negative}"

            outf.write(line)
            outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument(
        "--negative",
        "-n",
        type=Path,
    )
    oparser.add_argument(
        "--positive",
        "-p",
        type=Path,
    )
    oparser.add_argument("--config", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        path_positive_prompt=opts.positive,
        path_negative_prompt=opts.negative,
        path_config=opts.config,
    )


if __name__ == "__main__":
    main()
