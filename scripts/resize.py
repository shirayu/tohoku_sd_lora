#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Optional

from PIL import Image

Image.MAX_IMAGE_PIXELS = 100000000000


def resize(
    *,
    path_in: Path,
    path_out: Path,
    remove_alpha: bool,
    max_size: int,
    min_size: Optional[int],
) -> None:
    image = Image.open(str(path_in))

    if remove_alpha:
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            data = image.getdata()

            new_data = []
            for item in data:
                if item[3] == 0:
                    new_data.append((255, 255, 255, 255))  # white
                else:
                    new_data.append(item)
            image.putdata(new_data)
            image = image.convert("RGB")

    image = image.crop(image.getbbox())

    if image.width < max_size and image.height < max_size:
        pass
    else:
        if image.width > image.height:
            new_size = (
                max_size,
                int(image.height * max_size / image.width),
            )
        else:
            new_size = (
                int(image.width * max_size / image.height),
                max_size,
            )
        image = image.resize(new_size)

    if min_size is not None:
        assert min_size <= max_size
        new_x: int = max(image.width, min_size)
        new_y: int = max(image.height, min_size)
        new_image = Image.new(
            "RGB",
            (new_x, new_y),
            (255, 255, 255),
        )
        x_offset = (new_x - image.width) // 2
        y_offset = (new_y - image.height) // 2
        new_image.paste(image, (x_offset, y_offset))
        image = new_image

    image.save(str(path_out))


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--remove_alpha", action="store_true")
    oparser.add_argument("--size", type=int, required=True)
    oparser.add_argument("--min_size", type=int)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    resize(
        path_in=opts.input,
        path_out=opts.output,
        remove_alpha=opts.remove_alpha,
        max_size=opts.size,
        min_size=opts.min_size,
    )


if __name__ == "__main__":
    main()
