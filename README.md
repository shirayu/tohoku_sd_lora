
# tohoku_sd_preparation

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
[![CI](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/ci.yml/badge.svg)](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/ci.yml)
[![CodeQL](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/codeql-analysis.yml)
[![Typos](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/typos.yml/badge.svg)](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/typos.yml)

## Setup sd-scripts

```bash
git clone https://github.com/kohya-ss/sd-scripts.git ~/workspace/sd-scripts
cd ~/workspace/sd-scripts
python -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install bitsandbytes scipy lion_pytorch lycoris-lora xformers
```

## Setup images

- Install [poetry](https://python-poetry.org/)

```bash
# setup
poetry install

# Download images
poetry run python ./scripts/prepare/download.py -i ./data/urls -o ./data/img/original

# (Optional) If you want to also use special files
poetry run python ./scripts/prepare/download.py -i ./data/urls/_special -o ./data/img/original_special
# Convert files and place them to each folder under "data/img/original"


# Remove margins and shrink images
find data/img/original -type f | grep -v __misc | sort |xargs -t -P 4 -I {} poetry run python ./scripts/prepare/resize.py -i {} -o data/img/converted --size 2048 --to_dir

# Check files in "converted" with your eyes
# Add modificaion if you need

# Resize to 1024x1024 (max. min=768x768) and remove alphas
find data/img/converted -type f -name '*.png' | sort | xargs -t -P 4 -I {} poetry run python ./scripts/prepare/resize.py --remove_alpha -i {} -o data/img/train_1024 --size 1024 --min_size 768 --to_dir
```

### Chara

```bash
# Filter out
make -f ./train.mk prepare_for_chara

# train
make -f ./train.mk train_for_chara META3=./tmp/out/chara_with_style/meta_3/Zundamon.json

# tensorboard
make -f ./train.mk train_for_chara_tensorboard META3=./tmp/out/chara_with_style/meta_3/Zundamon.json
```

```bash
# Generation
bash -x ./scripts/gen_img.sh \
    BASE_MODEL.safetensors \
    OUTPUT_DIR \
    PROMPT_FILE.txt \
    LORA_FILE.safetensors
```

### Style

```bash
# Filter out
make -f ./train.mk prepare_for_style

# train
make -f ./train.mk train_for_style NUM_REPEATS=4

# merge (need much RAM)
make -f ./train.mk style_merge

# train preparation with it
make -f ./train.mk prepare_for_chara CHARA_WITHOUT_STYLE=1

# example of training
make -f ./train.mk train_for_chara \
    CHARA_WITHOUT_STYLE=1 \
    META3=tmp/out/chara_without_style/meta_3/Metan.json \
```

### Suffix

- ``oc``: Official costume
- ``_sd``: SD character

## Tagging

Use [img2tags](https://github.com/shirayu/img2tags)

```bash
img2tags --ext jsonl -i <(find ./data/img/train_1024/ -type f | sort ) -o /dev/stdout| python ./scripts/prepare/trim_tagger_result.py -o ./data/auto_tags.jsonl
```

## Check new URL

```bash
poetry run python ./scripts/prepare/get_urls.py --check ./data/img/original
```
