#!/usr/bin/env bash

set -x

REPO_ROOT=${SCRIPT_DIR:-"$(cd "$(dirname "$0")/../.." && pwd)"}
function print_stderr_msg() {
    printf "\e[31m%s\e[32m%s\e[m\n" "$1" "$2" 1>&2
}
export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export HF_DATASETS_OFFLINE=${HF_DATASETS_OFFLINE:-1}

SD_SCRIPTS_ROOT=${SD_SCRIPTS_ROOT:-~/workspace/sd-scripts}

if [[ $# -lt 2 ]]; then
    echo "[Usage] $0 basedir outputdir [param_train] [param_ds]" >/dev/stderr
    exit 1
fi

BASE_DIR="$1"
OUTPUT_DIR="$2"
PARAM_TRAIN="$3"
PARAM_DS="$4"
DIM=${DIM:-0}
SAMPLE_INTERVAL=${SAMPLE_INTERVAL:-0}
if [[ ${SAMPLE_INTERVAL} -eq 0 ]]; then
    ARG_SAMPLE=" --bool sample.sample_at_first=False --int sample.sample_every_n_steps=None --int sample.sample_every_n_epochs=None "
else
    ARG_SAMPLE=" --str 'sample.sample_prompts=${OUTPUT_DIR}/config/config_sample_prompts.txt' --int sample.sample_every_n_steps=${SAMPLE_INTERVAL}"
fi

test -e "${BASE_DIR}/base.safetensors"

LORA="${OUTPUT_DIR}/mymodel.safetensors"
if [ -e "${LORA}" ]; then
    print_stderr_msg "Already exist: " "${LORA}"
    exit
fi

META3=${META3:-${BASE_DIR}/meta_3.json}
test -e "${META3}"
test -e "${BASE_DIR}/images"

# config
if [[ ${DIM} -ne 0 ]]; then # LoRA
    NAG='[ "preset=full", "algo=lora"] '
    PARAM_LORA="--str lora.network_module=lycoris.kohya --int lora.network_dim=${DIM} --float lora.network_alpha=1 --jsonstr lora.network_args='${NAG}'"
fi

CONFIG_OUT_DIR="${OUTPUT_DIR}/config"
mkdir -p "${CONFIG_OUT_DIR}"
eval .venv/bin/python "${REPO_ROOT}/scripts/train_lora/rewrite_config.py" \
    -i ./data/config/config_train.toml \
    --str "save.output_dir=${OUTPUT_DIR}" \
    --str "save.logging_dir=${OUTPUT_DIR}/log" \
    --str "dataset.dataset_config=${OUTPUT_DIR}/config/config_dataset.toml" \
    "${ARG_SAMPLE}" \
    --str "model.pretrained_model_name_or_path=${BASE_DIR}/base.safetensors" \
    "${PARAM_LORA}" \
    -o "${CONFIG_OUT_DIR}/config_train.toml" \
    "${PARAM_TRAIN}" \
    || exit 8

cp "${META3}" "${CONFIG_OUT_DIR}/meta_3.json"

python "${REPO_ROOT}/scripts/train_lora/exclude_invalid_data_from_meta.py" \
    -i "${CONFIG_OUT_DIR}/meta_3.json" \
    -o "${CONFIG_OUT_DIR}/meta_4.json"

eval .venv/bin/python "${REPO_ROOT}/scripts/train_lora/rewrite_config.py" \
    -i ./data/config/config_dataset.toml \
    --str "datasets.subsets.image_dir=${BASE_DIR}/images" \
    --str "datasets.subsets.metadata_file=${CONFIG_OUT_DIR}/meta_4.json" \
    -o "${CONFIG_OUT_DIR}/config_dataset.toml" \
    "${PARAM_DS}" \
    || exit 9

# cp data/config/config_dataset.toml "${CONFIG_OUT_DIR}/config_dataset.toml"

cp data/config/config_accelerate.yaml "${CONFIG_OUT_DIR}/config_accelerate.yaml"
cp data/config/test_prompt* "${CONFIG_OUT_DIR}/"

# save version

mkdir -p "${OUTPUT_DIR}/version"
nvidia-smi --query-gpu=gpu_name,driver_version,compute_cap,memory.total --format=csv >"${OUTPUT_DIR}/version/gpu.csv"
~/workspace/sd-scripts/venv/bin/pip list --disable-pip-version-check | sed "s|$HOME|~|" >"${OUTPUT_DIR}/version/pip_list.txt"
git -C "${SD_SCRIPTS_ROOT}" show --format='%h' --no-patch >"${OUTPUT_DIR}/version/sd_scripts_version.txt"
grep '^#define CUDNN_MAJOR' -A2 /usr/include/*/cudnn_version.h >"${OUTPUT_DIR}/version/cudnn.txt"

TRAIN_SCRIPT="${SD_SCRIPTS_ROOT}/sdxl_train_network.py"
if [[ ${DIM} -eq 0 ]]; then # full fine-tuning
    TRAIN_SCRIPT="${SD_SCRIPTS_ROOT}/sdxl_train.py"
fi

eval "${SD_SCRIPTS_ROOT}/venv/bin/accelerate" \
    launch \
    --config_file "${CONFIG_OUT_DIR}/config_accelerate.yaml" \
    "${TRAIN_SCRIPT}" \
    --config_file "${CONFIG_OUT_DIR}/config_train.toml" \
    || exit 3

python "${REPO_ROOT}/scripts/train_lora/rename_output_filename.py" -i "${OUTPUT_DIR}/sample"
