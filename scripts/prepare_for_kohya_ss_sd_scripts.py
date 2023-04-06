#!/usr/bin/env python3

import argparse
import json
import shutil
from pathlib import Path
from typing import List, Optional, Set

STYLE_TRIGGER_WORD: str = "oistyle"
name2newname = {
    "melon": "Hokamel",
    "zunko_oc": "Zuoc",
    "kiritan_oc": "Kioc",
    "itako_oc": "Itoc",
}


def get_tags(
    *,
    path_target_dir: Path,
    target: Path,
    tag_root: Path,
) -> List[str]:
    root_dir: str = path_target_dir.name.replace("_oc__withchara", "_oc")
    tag_json_name: str = f"{target.stem}.json"
    if tag_json_name in {
        "zunmon001.json",
        "zunmon_3001.json",
        "zunmon_3002.json",
        "zunmon_3003.json",
        "zunmon_3004.json",
    }:
        root_dir = "zundamon_sd"

    with tag_root.joinpath(root_dir, tag_json_name).open() as tagf:
        tags: List[str] = json.load(tagf)
    return tags


def name2prompt(
    *,
    name: str,
    nosd: bool,
) -> Optional[str]:
    name = name.replace(".mod", "")
    items = name.split("_")

    prompt: str = name2newname.get(items[0], items[0])

    if "fairy" in items:
        assert prompt == "zundamon"
        prompt = "zfr"
    if "sd" in items:
        prompt += "_sd"
        if nosd:
            return

    if "oc" in items:
        c: str = prompt.split("_")[0]
        assert c in {"zunko", "kiritan", "itako"}
        prompt = name2newname[f"{c}_oc"]

    return prompt.capitalize()


def chara2class(chara: str) -> str:
    if chara.lower() == "zfr":
        return "chibi"
    if chara.lower() == "chuwa":
        return "no_humans"
    return "1girl"


def operate_one_file(
    *,
    path_target_dir: Path,
    target_image_file: Path,
    tag_root: Path,
    trigger_word: str,
    target_tags: Set[str],
    out_dir: Path,
):
    tags: List[str] = get_tags(
        path_target_dir=path_target_dir,
        target=target_image_file,
        tag_root=tag_root,
    )
    assert len(tags) > 0, f"Tags for `{target_image_file.stem}`  not found"

    # Add the trigger word
    new_tags = list(filter(lambda v: v not in target_tags, tags))
    new_tags.insert(0, trigger_word)

    # Output caption file
    to_caption = out_dir.joinpath(f"{target_image_file.stem}.txt")
    with to_caption.open("w") as of:
        of.write(", ".join(new_tags).replace("_", " "))
        of.write("\n")

    # Copy the image
    to = out_dir.joinpath(f"{target_image_file.name}")
    shutil.copy(target_image_file, to)


def operation_all(
    *,
    path_in: Path,
    path_out: Path,
    num_repeat: int,
    nosd: bool,
    tag_root: Path,
    tag_target: Path,  # 学習対象のタグ定義JSONファイル
) -> None:
    assert path_in.is_dir()

    assert tag_root.is_dir()

    with tag_target.open() as inf:
        chara2target_tags = json.load(inf)

    out_dir_style_name: str = f"{num_repeat}_gold"
    out_dir_style: Path = path_out.joinpath(STYLE_TRIGGER_WORD, out_dir_style_name)
    out_dir_style.mkdir(exist_ok=True, parents=True)

    for path_target_dir in path_in.iterdir():
        files = [fp for fp in path_target_dir.iterdir()]

        is_oc__with_chara: bool = False
        if "_oc__withchara" in path_target_dir.name:
            is_oc__with_chara = True

        chara = name2prompt(
            name=path_target_dir.name.replace("_oc__withchara", "_oc"),
            nosd=nosd,
        )
        if chara is None:
            print(f"{path_target_dir}\t{chara}: **SKIP**")
            continue
        if chara not in chara2target_tags:
            print(f"{path_target_dir}\t{chara}: **SKIP** because No chara2target_tags")
            continue

        out_dir_chara_name: str = f"{num_repeat}_gold"
        out_dir_chara: Path = path_out.joinpath(path_target_dir.name, out_dir_chara_name)
        out_dir_chara.mkdir(exist_ok=True, parents=True)

        target_tags: Set[str] = set(chara2target_tags[chara])
        if is_oc__with_chara:
            chara_body: str = {"Itoc": "Itako", "Zuoc": "Zunko", "Kioc": "Kiritan"}[chara]
            target_tags |= set(chara2target_tags[chara_body])

        trigger_word: str = chara.capitalize()
        if is_oc__with_chara:
            trigger_word = {"Itoc": "ItakoOC", "Zuoc": "ZunkoOC", "Kioc": "KiritanOC"}[trigger_word]

        print(f"{path_target_dir}\t{chara.capitalize()}: {len(files)}")
        for target_image_file in files:
            operate_one_file(
                path_target_dir=path_target_dir,
                target_image_file=target_image_file,
                tag_root=tag_root,
                trigger_word=chara,
                target_tags=target_tags,
                out_dir=out_dir_chara,
            )
            operate_one_file(
                path_target_dir=path_target_dir,
                target_image_file=target_image_file,
                tag_root=tag_root,
                trigger_word=STYLE_TRIGGER_WORD,
                target_tags=set(),
                out_dir=out_dir_style,
            )


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--tag", type=Path, required=True)
    oparser.add_argument("--tag-target", type=Path, required=True)
    oparser.add_argument("--repeat", type=int, default=1)
    oparser.add_argument("--nosd", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation_all(
        path_in=opts.input,
        path_out=opts.output,
        num_repeat=opts.repeat,
        nosd=opts.nosd,
        tag_root=opts.tag,
        tag_target=opts.tag_target,
    )


if __name__ == "__main__":
    main()
