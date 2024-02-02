#!/usr/bin/env python3
import argparse
import json
from distutils.util import strtobool
from pathlib import Path

import toml


def set_value(d: dict, key: str, val):
    ks: list[str] = key.split(".")
    if len(ks) == 1:
        d[ks[0]] = val
        return
    elif len(ks) == 2:
        if ks[0] not in d:
            d[ks[0]] = {ks[1]: val}
        elif isinstance(d[ks[0]], list):
            for v in d[ks[0]]:
                assert ks[1] in v
                v[ks[1]] = val
        else:
            d[ks[0]][ks[1]] = val
        return

    if isinstance(d[ks[0]], list):
        for v in d[ks[0]]:
            set_value(
                v,
                ".".join(ks[1:]),
                val,
            )
    else:
        set_value(
            d[ks[0]],
            ".".join(ks[1:]),
            val,
        )


def operation(
    *,
    path_in: Path,
    path_out: Path,
    args_float: list[str],
    args_int: list[str],
    args_str: list[str],
    args_jsonstr: list[str],
    args_bool: list[str],
) -> None:
    with path_in.open() as inf:
        d = toml.load(inf)

    for arg in args_float:
        kv = arg.split("=", maxsplit=1)
        set_value(
            d,
            kv[0],
            float(kv[1]) if kv[1] != "None" else None,
        )

    for arg in args_int:
        kv = arg.split("=", maxsplit=1)
        set_value(
            d,
            kv[0],
            int(kv[1]) if kv[1] != "None" else None,
        )

    for arg in args_str:
        kv = arg.split("=", maxsplit=1)
        set_value(
            d,
            kv[0],
            str(kv[1]) if kv[1] != "None" else None,
        )

    for arg in args_jsonstr:
        kv = arg.split("=", maxsplit=1)
        set_value(
            d,
            kv[0],
            json.loads(kv[1]) if kv[1] != "None" else None,
        )

    for arg in args_bool:
        kv = arg.split("=", maxsplit=1)
        set_value(
            d,
            kv[0],
            bool(strtobool(kv[1])) if kv[1] != "None" else None,
        )

    with path_out.open("w") as outf:
        toml.dump(d, outf)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)

    oparser.add_argument(
        "--float",
        action="append",
        default=[],
    )
    oparser.add_argument(
        "--int",
        action="append",
        default=[],
    )
    oparser.add_argument(
        "--str",
        action="append",
        default=[],
    )
    oparser.add_argument(
        "--jsonstr",
        action="append",
        default=[],
    )
    oparser.add_argument(
        "--bool",
        action="append",
        default=[],
    )

    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_in=opts.input,
        path_out=opts.output,
        args_float=opts.float,
        args_int=opts.int,
        args_str=opts.str,
        args_jsonstr=opts.jsonstr,
        args_bool=opts.bool,
    )


if __name__ == "__main__":
    main()
