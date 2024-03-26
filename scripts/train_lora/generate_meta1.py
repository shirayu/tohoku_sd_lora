#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Final

from pydantic import BaseModel

STYLE_TRIGGER_WORD: str = "oistyle"


def trim_tag(v: str) -> str:
    if len(v) <= 3:
        return v
    return v.replace("_", " ")


FIRST_GENERAL_TAGS: Final[set[str]] = set(
    "1girl|2girls|3girls|4girls|5girls|6+girls|multiple girls"
    "|1boy|2boys|3boys|4boys|5boys|6+boys|multiple boys|male focus".split("|")
)

BANNED_TAGS: Final[set[str]] = {
    "personification",
    "virtual_youtuber",
    "transparent_background",
}


class AllTag(BaseModel):
    first_general_tags: list[str]
    rating: str | None = None
    rest_general_tags: list[str]

    @staticmethod
    def parse_tags(d: dict) -> "AllTag":
        rating: str | None = None
        myrating_val: float = -1
        for k, v in d["tags"]["9"].items():
            if v > myrating_val:
                myrating_val = v
                rating = k

        auto_tags: set[str] = set(d["tags"]["0"].keys())

        # banned tags
        my_rest_general_tags: list[str] = []
        my_first_general_tags: set[str] = set()
        for t in auto_tags:
            if t.startswith("alternate_") or t in BANNED_TAGS:
                continue
            if t in FIRST_GENERAL_TAGS:
                my_first_general_tags.add(t)
                continue

            my_rest_general_tags.append(t)

        return AllTag(
            first_general_tags=sorted(list(my_first_general_tags)),
            rating=rating,
            rest_general_tags=my_rest_general_tags,
        )


def operation(
    *,
    path_in: Path,
    path_out: Path,
    path_tag: Path,
    path_tag_group: Path,
    path_trigger: Path,  # 学習対象のタグ定義JSONファイル
    for_style: bool,
    no_style_trigger_word: bool,
    path_output_trigger: Path | None,
    force_girl: bool = True,
) -> None:
    fanme2alltags: dict[str, AllTag] = {}

    with path_tag.open() as inf:
        for line in inf:
            d = json.loads(line)
            fname: str = Path(d["input"]).stem

            p: str = Path(d["input"]).parent.name
            key: str = f"{p}___{fname}"
            fanme2alltags[key] = AllTag.parse_tags(d)
            if force_girl:
                fanme2alltags[key].first_general_tags = [
                    v.replace("boy", "girl") for v in fanme2alltags[key].first_general_tags
                ]

    group2tags: dict[str, set[str]] = {}
    for f in path_tag_group.glob("**/*.txt"):
        with f.open() as inf:
            group2tags[f.stem] = set()
            for line in inf:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"):
                    continue
                group2tags[f.stem].add(line)

    chara2target_tags: dict[str, set[str]] = {}
    with path_trigger.open() as inf:
        for k, gs in json.load(inf).items():
            chara2target_tags[k] = set()
            for group in gs:
                chara2target_tags[k] |= group2tags[group]

    fname2caption: dict[str, dict[str, str]] = {}
    dirname2trigger: dict[str, dict[str, str]] = {}
    for imgf in path_in.iterdir():
        chara: str = imgf.stem.split("___")[0].replace(".mod", "")

        is_oc__with_chara: bool = False
        if "__withchara" in imgf.stem:
            is_oc__with_chara = True

        target_tags: set[str] = chara2target_tags[chara.replace("_sd", "").replace("__withchara", "")]
        if is_oc__with_chara:
            chara_body: str = {
                "Itoc": "Itako",
                "Zuoc": "Zunko",
                "Kioc": "Kiritan",
                "Meoc": "Metan",
            }[chara.replace("__withchara", "")]
            target_tags |= chara2target_tags[chara_body]
        if "_sd" in chara:
            target_tags.add("chibi")

        trigger_word: str = chara
        if is_oc__with_chara:
            trigger_word = {
                "Itoc": "ItakoOC",
                "Zuoc": "ZunkoOC",
                "Kioc": "KiritanOC",
                "Meoc": "MetanOC",
            }[trigger_word.replace("__withchara", "")]
        elif trigger_word.endswith("oc"):
            trigger_word = f"1girl wear {trigger_word}"

        # Add the trigger word
        myalltag: AllTag = fanme2alltags[imgf.stem.replace("__withchara", "")]
        new_tags_rest_general_tags: list[str]
        if for_style:
            new_tags_rest_general_tags = list(myalltag.rest_general_tags)
        else:
            new_tags_rest_general_tags = list(filter(lambda v: v not in target_tags, myalltag.rest_general_tags))

        triggers: list[str] = []
        if not for_style:
            triggers.append(trigger_word)
        trigger_for_generate: str = ", ".join(triggers)
        if not no_style_trigger_word:
            triggers.append(STYLE_TRIGGER_WORD)

        caption: str = ""
        if len(myalltag.first_general_tags) > 0:
            caption += ", ".join(myalltag.first_general_tags)
            caption += ", "

        trigger_for_train: str = ", ".join(triggers)
        caption += f"{trigger_for_train}"

        if myalltag.rating:
            caption += f", rating: {myalltag.rating}"

        # https://github.com/kohya-ss/sd-scripts/pull/975
        caption += ", |||"

        trimmed_new_tags: list[str] = sorted([trim_tag(v) for v in new_tags_rest_general_tags])
        caption += ", ".join(trimmed_new_tags)
        fname2caption[imgf.stem] = {
            "caption": caption,
        }
        dirname2trigger[imgf.stem.split("___")[0]] = {
            "train": trigger_for_train,
            "generate": trigger_for_generate,
        }

    with path_out.open("w") as outf:
        outf.write(
            json.dumps(
                fname2caption,
                ensure_ascii=False,
                sort_keys=True,
                indent=4,
            )
        )
        outf.write("\n")

    if path_output_trigger is not None:
        with path_output_trigger.open("w") as outf:
            outf.write(
                json.dumps(
                    dirname2trigger,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=4,
                )
            )
            outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--output_triggers", type=Path, required=False)
    oparser.add_argument("--tag", type=Path, required=True)
    oparser.add_argument("--tag-trigger", type=Path, required=True)
    oparser.add_argument("--tag-group", type=Path, required=True)
    oparser.add_argument("--for_style", action="store_true")
    oparser.add_argument("--no_style_trigger_word", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        path_output_trigger=opts.output_triggers,
        path_tag=opts.tag,
        path_tag_group=opts.tag_group,
        path_trigger=opts.tag_trigger,
        for_style=opts.for_style,
        no_style_trigger_word=opts.no_style_trigger_word,
    )


if __name__ == "__main__":
    main()
