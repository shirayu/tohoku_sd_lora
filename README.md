
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
./venv/bin/pip install bitsandbytes scipy lion_pytorch
./venv/bin/pip install xformers
```

## Setup images

- Install [poetry](https://python-poetry.org/)

```bash
# setup
poetry install

# Download images
poetry run python scripts/download.py -i ./data/urls -o ./data/img/original

# (Optional) If you want to also use special files
poetry run python scripts/download.py -i ./data/urls/_special -o ./data/img/original_special
# Convert files and place them to each folder under "data/img/original"


# Remove margins and shrink images
find data/img/original -type f | xargs -t -P 4 -I {} poetry run python ./scripts/resize.py -i {} -o data/img/converted --size 2048 --to_dir

# Check files in "img_converted" with your eyes
# Add modificaion if you need

# Resize to 1024x1024 (max. min=768x768) and remove alphas
find data/img/converted -type f -name '*.png' | xargs -t -P 4 -I {} poetry run python ./scripts/resize.py --remove_alpha -i {} -o data/img/train_1024 --size 1024 --min_size 768 --to_dir

# Filter out
python ./scripts/filtered_mksymlink.py --ex ./data/exclude_images.tsv -i ./data/img/train_1024 -o ./data/img/train_1024_filtered

# meta_1
python ./scripts/generate_meta1.py --tag ./data/img/train_1024_filtered.tags.jsonl --tag-target ./data/tag_target.json -i ./data/img/train_1024_filtered -o ./data/img/meta_1.json

# meta_2
~/workspace/sd-scripts/venv/bin/python \
    ~/workspace/sd-scripts/finetune/prepare_buckets_latents.py \
    ./data/img/train_1024_filtered \
    ./data/img/meta_1.json \
    ./data/img/meta_2.json \
    ~/data/sd/models/_base/animagine-xl-3.0-base.safetensors \
    --mixed_precision bf16 \
    --min_bucket_reso 512 \
    --max_resolution 1024,1024 \
    --max_bucket_reso 1568 \
    --batch_size 4

# meta_3
python ./scripts/generate_meta3.py -i ./data/img/meta_2.json -o ./data/img/meta_3
```

### Prefix

- ``_oc``: Official costume
- ``_sd``: SD character

## Tagging

Use [img2tags](https://github.com/shirayu/img2tags)

```bash
img2tags --ext jsonl -i ./data/img/train_1024_filtered -o ./data/img/train_1024_filtered.tags.jsonl
```

## Check new URL

```bash
poetry run python ./scripts/get_urls.py | cat - ./data/urls/*txt ./data/urls/_special/* | sort | uniq -c | sort -k1nr | grep -v psd | grep -v ai$ | grep -v '2 '
```
