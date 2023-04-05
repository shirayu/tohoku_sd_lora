#!/usr/bin/env python3

import argparse
import json
import shutil
from pathlib import Path
from typing import List, Optional, Set

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


def operation(
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

        out_dir_name: str = f"{num_repeat}_gold"
        out_dir: Path = path_out.joinpath(path_target_dir.name, out_dir_name)
        out_dir.mkdir(exist_ok=True, parents=True)

        target_tags: Set[str] = set(chara2target_tags[chara])
        if is_oc__with_chara:
            chara_body: str = {"Itoc": "Itako", "Zuoc": "Zunko", "Kioc": "Kiritan"}[chara]
            target_tags |= set(chara2target_tags[chara_body])

        print(f"{path_target_dir}\t{chara.capitalize()}: {len(files)}")
        for tgt in files:
            tags: List[str] = get_tags(
                path_target_dir=path_target_dir,
                target=tgt,
                tag_root=tag_root,
            )
            if len(tags) == 0:
                raise KeyError(f"Tags for `{tgt.stem}` in `{chara}` not found")

            new_tags = list(filter(lambda v: v not in target_tags, tags))
            if is_oc__with_chara:
                new_tags.insert(0, {"Itoc": "ItakoOC", "Zuoc": "ZunkoOC", "Kioc": "KiritanOC"}[chara])
            else:
                new_tags.insert(0, chara.capitalize())

            to_caption = out_dir.joinpath(f"{tgt.stem}.txt")
            with to_caption.open("w") as of:
                of.write(", ".join(new_tags).replace("_", " "))
                of.write("\n")

            to = out_dir.joinpath(f"{tgt.name}")
            shutil.copy(tgt, to)


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
    operation(
        path_in=opts.input,
        path_out=opts.output,
        num_repeat=opts.repeat,
        nosd=opts.nosd,
        tag_root=opts.tag,
        tag_target=opts.tag_target,
    )


if __name__ == "__main__":
    main()
