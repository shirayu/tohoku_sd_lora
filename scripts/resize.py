#!/usr/bin/env python3

import argparse
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = 100000000000


def operation(
    *,
    path_in: Path,
    path_out: Path,
    max_size: int = 2048,
) -> None:
    input_image = Image.open(str(path_in))
    input_image = input_image.crop(input_image.getbbox())

    if input_image.width < max_size and input_image.height < max_size:
        pass
    else:
        if input_image.width > input_image.height:
            new_size = (
                max_size,
                int(input_image.height * max_size / input_image.width),
            )
        else:
            new_size = (
                int(input_image.width * max_size / input_image.height),
                max_size,
            )
        input_image = input_image.resize(new_size)
    input_image.save(str(path_out))


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
