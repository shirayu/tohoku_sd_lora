
# tohoku_sd_preparation

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
[![CI](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/ci.yml/badge.svg)](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/ci.yml)
[![CodeQL](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/codeql-analysis.yml)
[![Typos](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/typos.yml/badge.svg)](https://github.com/shirayu/tohoku_sd_preparation/actions/workflows/typos.yml)

## Setup sd-scripts

- Install [poetry](https://python-poetry.org/)

```bash
git clone https://github.com/kohya-ss/sd-scripts.git ~/repo/sd-scripts
cp ./config/* ~/repo/sd-scripts
cd ~/repo/sd-scripts
poetry install
```

## Setup images

```bash
# Install ImageMagick
sudo apt-get -y install imagemagic

# Edit the setting of ImageMagick TEMPORALLY (Resotre after conversion)
sudo cp /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.backup
sudo vi /etc/ImageMagick-6/policy.xml
##  <policy domain="resource" name="memory" value="8GiB"/>
##  <policy domain="resource" name="map" value="8GiB"/>
##  <policy domain="resource" name="width" value="160KP"/>
##  <policy domain="resource" name="height" value="160KP"/>
##  <policy domain="resource" name="area" value="8GiB"/>
##  <policy domain="resource" name="disk" value="8GiB"/>


# setup
poetry install

# Download images
poetry run python scripts/download.py -i ./url_list -o ./data/img_original

# (Optional) If you want to also use special files
poetry run python scripts/download.py -i ./url_list/_special -o ./data/img_original_special
# Convert files and place them to each folder under "data/img_original"


# Remove margins and shrink images
find data/img_original -type f | xargs -t -P 4 -I {} bash ./scripts/convert_image_0.sh {} data/img_converted

# Check files in "img_converted" with your eyes
# Add modificaion if you need

# Resize to 862x862 (max. min=768x768) and remove alphas
find data/img_converted -type f -name '*.png' | xargs -t -P 4 -I {} bash ./scripts/convert_image_1.sh {} data/img_train_862 862 768

# Filter out
python ./scripts/filtered_copy.py --ex ./target_list/exclude.tsv -i ./data/img_train_862 -o ./data/img_train_862_filtered

# Generate captions
python ./scripts/prepare_for_kohya_ss_sd_scripts.py -i ./data/img_train_862_filtered -o ./data/img_train_862_filtered_for_train --nosd --repeat 10 --tag ./data/tag/tags_json --tag-target ./data/tag/tag_target.json

# Generate train scripts
## "--caption" is optional
python ./scripts/prepare_for_kohya_ss_sd_cmd.py \
    -i ./data/img_train_862_filtered_for_train \
    --resolution 862 \
    -o ./data/trained_lora_models \
    -C ~/repo/sd-scripts \
    --v2 --v_parameterization \
    --model ~/data/sd-webui-models/Stable-diffusion/wd-1-5-beta2-fp16.safetensors \
    --caption \
    --lr_scheduler='constant' \
    --lr 1e-4 \
    --text_encoder_lr 5e-5 \
    --dim 32 --alpha 16 \
    --bs 1 \
    --epoch 10

# If you want to use genberate regularization images to the following directories and add "--reg ./data/img_reg_ModelName"
# - data/img_reg_ModelName/chibi/1_chibi
# - data/img_reg_ModelName/1girl/1_1girl
```

### Prefix

- ``_oc``: Official costume
- ``_sd``: SD character

## Tags

```bash
find /path/to/images -mindepth 1 -type d | sort | parallel -t -n1 -P1 --lb poetry run python -m finetune.tag_images_by_wd14_tagger --batch_size=4
python ./scripts/tag2json.py -i /path/to/images -o ./data/tag/tags_json 
```