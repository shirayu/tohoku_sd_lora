#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

STYLE_TRIGGER_WORD: str = "oistyle"
NAME2NEWNAME = {
    "melon": "Hokamel",
    "zunko_oc": "Zuoc",
    "kiritan_oc": "Kioc",
    "itako_oc": "Itoc",
    "metan_oc": "Metan",
}


def name2chara(name: str) -> str:
    name = name.replace(".mod", "")
    items = name.split("_")

    prompt: str = NAME2NEWNAME.get(items[0], items[0])

    if "fairy" in items:
        assert prompt == "zundamon"
        prompt = "zfr"
    if "sd" in items:
        prompt += "_sd"

    if "oc" in items:
        c: str = prompt.split("_")[0]
        prompt = NAME2NEWNAME[f"{c}_oc"]

    return prompt.capitalize()


def operation(
    *,
    path_in: Path,
    path_out: Path,
    path_tag: Path,
    path_tag_target: Path,  # 学習対象のタグ定義JSONファイル
) -> None:
    fanme2alltags: dict[str, set[str]] = {}
    with path_tag.open() as inf:
        for line in inf:
            d = json.loads(line)
            fname: str = Path(d["input"]).stem
            tags: set[str] = set(d["tags"]["0"].keys())
            fanme2alltags[fname] = tags

    with path_tag_target.open() as inf:
        chara2target_tags: dict[str, list[str]] = json.load(inf)

    fname2caption: dict[str, dict[str, str]] = {}
    for imgf in path_in.iterdir():
        name: str = imgf.stem.split("___")[0]
        chara: str = name2chara(name)

        tags_for_imgf: None | set[str] = fanme2alltags.get(imgf.stem)
        if tags_for_imgf is None:
            print(f"{imgf}: **SKIP** because No chara2target_tags")
            continue

        is_oc__with_chara: bool = False
        if "_oc__withchara" in imgf.stem:
            is_oc__with_chara = True

        target_tags: set[str] = set(chara2target_tags[chara.replace("_sd", "")])
        if is_oc__with_chara:
            chara_body: str = {
                "Itoc": "Itako",
                "Zuoc": "Zunko",
                "Kioc": "Kiritan",
                "Metan": "Metan",
            }[chara]
            target_tags |= set(chara2target_tags[chara_body])

        trigger_word: str = chara.capitalize()
        if is_oc__with_chara:
            trigger_word = {
                "Itoc": "ItakoOC",
                "Zuoc": "ZunkoOC",
                "Kioc": "KiritanOC",
                "Metan": "Metan",
            }[trigger_word]

        # Add the trigger word
        new_tags = list(filter(lambda v: v not in target_tags, tags_for_imgf))
        triggers: list[str] = []
        triggers.append(trigger_word)
        if trigger_word != STYLE_TRIGGER_WORD:
            triggers.append(STYLE_TRIGGER_WORD)

        # https://github.com/kohya-ss/sd-scripts/pull/975
        caption = ", ".join(triggers) + ", ||| " + ", ".join(new_tags)
        fname2caption[imgf.stem] = {
            "caption": caption,
        }

    with path_out.open("w") as outf:
        outf.write(
            json.dumps(
                fname2caption,
                ensure_ascii=False,
                indent=4,
            )
        )
        outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--tag", type=Path, required=True)
    oparser.add_argument("--tag-target", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        path_tag=opts.tag,
        path_tag_target=opts.tag_target,
    )


if __name__ == "__main__":
    main()
