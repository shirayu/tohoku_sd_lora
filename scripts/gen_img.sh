#!/usr/bin/env bash
SD_SCRIPTS_ROOT=~/workspace/sd-scripts
REPO_ROOT=${SCRIPT_DIR:-"$(cd "$(dirname "$0")/.." && pwd)"}
function print_stderr_msg() {
    printf "\e[31m%s\e[32m%s\e[m\n" "$1" "$2" 1>&2
}
export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export HF_DATASETS_OFFLINE=${HF_DATASETS_OFFLINE:-1}

if [[ $# -lt 3 ]]; then
    print_stderr_msg "[Usage] " "$0 <model_file> <prompt_file> <output_dir> [<LoRA_file>]"
    exit 1
fi

MODEL_FILE=${1}
PROMPT_FILE=${2}
OUTPUT_DIR=${3}
LORA=${4}
if [[ ${LORA} != "" ]]; then
    ARG_LORA="--network_module networks.lora --network_weights ${LORA}"
fi

mkdir -p "${OUTPUT_DIR}"

eval "${SD_SCRIPTS_ROOT}/venv/bin/python" \
    "${SD_SCRIPTS_ROOT}/sdxl_gen_img.py" \
    --ckpt "${MODEL_FILE}" \
    --seed 0 \
    --scale 7 \
    --sampler euler_a \
    --steps 30 \
    --outdir "${OUTPUT_DIR}" \
    --xformers \
    --W 896 \
    --H 1152 \
    --bf16 \
    --batch_size 1 \
    --from_file "${PROMPT_FILE}" \
    "${ARG_LORA}"
