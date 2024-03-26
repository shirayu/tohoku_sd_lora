#!/usr/bin/env python3

import argparse
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = 100000000000


def resize(
    *,
    path_in: Path,
    path_out: Path,
    remove_alpha: bool,
    max_size: int,
    min_size: int | None,
    to_dir: bool,
) -> None:
    if to_dir:
        root = path_out.joinpath(path_in.parent.name)
        root.mkdir(exist_ok=True, parents=True)
        path_out = root.joinpath(path_in.name)

    image = Image.open(str(path_in))

    if remove_alpha:
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            new_image = Image.new("RGBA", image.size, "#FFF")
            new_image.paste(image, (0, 0), image)
            image = new_image.convert("RGB")

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
            image = image.resize(
                new_size,
                resample=Image.Resampling.LANCZOS,
            )

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
    oparser.add_argument("--to_dir", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    resize(
        path_in=opts.input,
        path_out=opts.output,
        remove_alpha=opts.remove_alpha,
        max_size=opts.size,
        min_size=opts.min_size,
        to_dir=opts.to_dir,
    )


if __name__ == "__main__":
    main()
