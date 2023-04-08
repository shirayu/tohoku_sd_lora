#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Optional


def chara2class(chara: str) -> str:
    if chara.lower() == "zfr":
        return "chibi"
    return "1girl"


def operation(
    *,
    path_in: Path,
    path_out: Path,
    path_model: Path,
    path_reg: Optional[Path],
    path_script_dir: Path,
    use_caption: bool,
    dim: int,
    alpha=int,
    clip_skip: int,
    vae_batch_size: int,
    lr: str,
    lr_scheduler: str,
    lr_warmup_steps: int,
    unet_lr: str,
    text_encoder_lr: str,
    epoch: int,
    resolution: str,
    optimizer_arg: Optional[str],
    bs: int,
    interval: int,
    v2: bool,
    v_parameterization: bool,
    keep_tokens: int,
) -> None:
    assert path_in.exists()
    assert path_script_dir.exists()
    assert path_script_dir.exists()
    path_out.mkdir(exist_ok=True, parents=True)

    if optimizer_arg is None:
        optimizer_arg = "--use_8bit_adam"
    #         optimizer_arg = '--optimizer_type=adafactor --optimizer_args --lr_scheduler="constant_with_warmup" '

    arg_v2: str = ""
    if v2:
        arg_v2 = "--v2"
        print("[info] --v2: Check whiter --v_parameterization is needed or not")
    if v_parameterization:
        arg_v2 += " --v_parameterization "

    arg_clip = ""
    if clip_skip is not None:
        if v2:
            raise Exception("[*] v2 with clip_skip will be unexpected")
        else:
            arg_clip = f"--clip_skip={clip_skip} "
    for pathdir in path_in.iterdir():
        if not pathdir.is_dir():
            continue
        chara: str = pathdir.name
        path_out_chara = path_out.joinpath(chara)

        assert path_model.is_file()
        fullpath_model: str = str(path_model.absolute())
        fullpath_log: str = str(path_out_chara.joinpath("log").absolute())
        fullpath_train: str = str(pathdir.absolute())
        opt_fullpath_reg: str = ""
        if path_reg is not None:
            x = [z for z in path_reg.glob("*/*")]
            assert len(x) > 0, f"No files in {path_reg}"
            opt_fullpath_reg = f"--reg_data_dir={path_reg.joinpath(chara2class(chara)).absolute()}"

        opt_captiopn: str = ""
        if use_caption:
            opt_captiopn = f"""--shuffle_caption --keep_tokens {keep_tokens} --caption_extension=".txt" """

        CONTENT: str = f"""cd {path_script_dir.absolute()}

if [[ -e {path_out_chara.absolute()}/last.safetensors ]]; then
    exit 0
fi

poetry run \\
    accelerate launch \\
    --num_processes 1 \\
    --num_machines 1 \\
    --mixed_precision "fp16" \\
    --dynamo_backend "no" \\
    train_network.py \\
    --pretrained_model_name_or_path={fullpath_model} \\
    --logging_dir={fullpath_log} \\
    --train_data_dir={fullpath_train} \\
    --output_dir={path_out_chara.absolute()} \\
    --prior_loss_weight=1.0 \\
    --train_batch_size={bs} \\
    --lr_warmup_steps={lr_warmup_steps} \\
    --lr_scheduler='{lr_scheduler}' \\
    --learning_rate={lr} \\
    --unet_lr={unet_lr} \\
    --text_encoder_lr={text_encoder_lr} \\
    --max_train_epochs={epoch} \\
    {optimizer_arg} \\
    --xformers \\
    --mixed_precision=fp16 \\
    --save_every_n_epochs={interval} \\
    {arg_v2} \\
    {arg_clip} \\
    --seed=42 \\
    --network_dim={dim} \\
    --network_alpha={alpha} \\
    --network_module=networks.lora \\
    --save_model_as=safetensors \\
    --save_precision="fp16" \\
    --resolution="{resolution}" \\
    --min_bucket_reso 256 \\
    --max_bucket_reso {resolution} \\
    {opt_fullpath_reg} \\
    --enable_bucket \\
    --bucket_reso_steps 64 \\
    --max_data_loader_n_workers=4 \\
    --persistent_data_loader_workers \\
    {opt_captiopn} \\
    --vae_batch_size {vae_batch_size} \\
    """
        #     --no_metadata

        path_out_chara.mkdir(exist_ok=True, parents=True)
        with path_out_chara.joinpath(f"{pathdir.name}_train.sh").open("w") as outf:
            outf.write(CONTENT)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--model", type=Path, required=True)
    oparser.add_argument("--reg", type=Path)
    oparser.add_argument("--script-dir", "-C", type=Path, required=True)
    oparser.add_argument("--caption", action="store_true")
    oparser.add_argument("--dim", type=int, required=True)
    oparser.add_argument("--alpha", type=int, required=True)
    oparser.add_argument("--clip_skip", type=int, default=None)
    oparser.add_argument("--vae_batch_size", type=int, default=2)
    oparser.add_argument("--lr_scheduler", type=str, required=True)
    oparser.add_argument("--lr_warmup_steps", type=int, default=0)
    oparser.add_argument("--lr", type=str, required=True)
    oparser.add_argument("--unet_lr", type=str)
    oparser.add_argument("--text_encoder_lr", type=str)
    oparser.add_argument("--epoch", type=int, required=True)
    oparser.add_argument("--resolution", type=str, required=True)
    oparser.add_argument("--optimizer_arg", type=str, default=None)
    oparser.add_argument("--bs", type=int, default=1)
    oparser.add_argument("--interval", type=int, default=1)
    oparser.add_argument("--v2", action="store_true")
    oparser.add_argument("--v_parameterization", action="store_true")
    oparser.add_argument("--keep_tokens", type=int, default=2)

    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    if opts.unet_lr is None:
        opts.unet_lr = opts.lr
    if opts.text_encoder_lr is None:
        opts.text_encoder_lr = opts.lr

    operation(
        path_in=opts.input,
        path_out=opts.output,
        path_model=opts.model,
        path_reg=opts.reg,
        path_script_dir=opts.script_dir,
        use_caption=opts.caption,
        dim=opts.dim,
        alpha=opts.alpha,
        clip_skip=opts.clip_skip,
        vae_batch_size=opts.vae_batch_size,
        lr=opts.lr,
        lr_scheduler=opts.lr_scheduler,
        lr_warmup_steps=opts.lr_warmup_steps,
        unet_lr=opts.unet_lr,
        text_encoder_lr=opts.text_encoder_lr,
        epoch=opts.epoch,
        resolution=opts.resolution,
        optimizer_arg=opts.optimizer_arg,
        bs=opts.bs,
        interval=opts.interval,
        v2=opts.v2,
        v_parameterization=opts.v_parameterization,
        keep_tokens=opts.keep_tokens,
    )


if __name__ == "__main__":
    main()
