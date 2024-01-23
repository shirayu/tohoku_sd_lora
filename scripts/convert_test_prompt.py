#!/usr/bin/env python3

import argparse
from pathlib import Path

COMMON_NEGATIVE: str = """lowres, bad anatomy, bad hands, text, error, missing fingers,
extra digit, fewer digits, cropped, worst quality, low quality,
normal quality, jpeg artifacts, signature, watermark, username, blurry"""
COMMON_NEGATIVE = ", ".join([v.strip() for v in COMMON_NEGATIVE.replace("\n", "").split(", ")])


def operation(
    *,
    path_in: Path,
    path_out: Path,
    negative_prompt: str,
    scale: float = 7.0,
    step: int = 30,
    seed: int = 1234,
) -> None:
    with path_in.open() as inf, path_out.open("w") as outf:
        for line in inf:
            line = line.strip()

            if line.startswith("#") or len(line) == 0:
                continue

            if " --d " not in line:
                line += f" --d {seed}"
            if " --l " not in line:
                line += f" --l {scale}"
            if " --s " not in line:
                line += f" --s {step}"
            if " --n " not in line:
                line += f" --n {COMMON_NEGATIVE}"

            outf.write(line)
            outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--negative", "-n", default=COMMON_NEGATIVE)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        negative_prompt=opts.negative,
    )


if __name__ == "__main__":
    main()
