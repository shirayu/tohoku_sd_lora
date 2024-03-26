#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

COMMON_NEGATIVE: str = """lowres, bad anatomy, bad hands, text, error, missing fingers,
extra digit, fewer digits, cropped, worst quality, low quality,
normal quality, jpeg artifacts, signature, watermark, username, blurry"""
COMMON_NEGATIVE = ", ".join([v.strip() for v in COMMON_NEGATIVE.replace("\n", "").split(", ")])

COMMON_POSITIVE: str = """intricate details, high resolution, masterpiece, best quality"""


def operation(
    *,
    path_in: Path,
    path_out: Path,
    negative_prompt: str,
    scale: float = 7.0,
    step: int = 30,
    seed: int = 1234,
    path_config: Path,
) -> None:
    with path_config.open() as inf:
        config = json.load(inf)
        trigger: str = config["trigger_info"]["generate"]

    with path_in.open() as inf, path_out.open("w") as outf:
        for line in inf:
            line = line.strip().replace("<trigger>", trigger).replace("<positive_quality>", COMMON_POSITIVE)

            if line.startswith("#") or len(line) == 0:
                continue

            if " --d " not in line:
                line += f" --d {seed}"
            if " --l " not in line:
                line += f" --l {scale}"
            if " --s " not in line:
                line += f" --s {step}"
            if " --n " not in line:
                line += f" --n {negative_prompt}"

            outf.write(line)
            outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--negative", "-n", default=COMMON_NEGATIVE)
    oparser.add_argument("--config", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        negative_prompt=opts.negative,
        path_config=opts.config,
    )


if __name__ == "__main__":
    main()
