#!/usr/bin/env bash
SD_SCRIPTS_ROOT=~/workspace/sd-scripts

export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export HF_DATASETS_OFFLINE=${HF_DATASETS_OFFLINE:-1}

if [[ $# -lt 1 ]]; then
    echo "No model name is given" 2>&1
    exit 1
fi

LORA=${LORA:-}
if [[ ${LORA} != "" ]]; then
    ARG_LORA="--network_module networks.lora --network_weights ${LORA}"
fi
PROMPT_PREFIX=${PROMPT_PREFIX:-}

OUTPUT_DIR_ROOT=${OUTPUT_DIR_ROOT:-tmp/generated_images}
mkdir -p "${OUTPUT_DIR_ROOT}"
python ./scripts/convert_test_prompt.py \
    -i "data/config/test_prompt.txt" \
    -o "${OUTPUT_DIR_ROOT}/prompts.txt" \
    --prefix "${PROMPT_PREFIX}" \
    || exit 10

for FILENAME in "$@"; do

    STEM=$(echo "${FILENAME}" | sed 's|.*/||; s|.[^\.]*$||')
    OUTPUT_DIR="${OUTPUT_DIR_ROOT}/${STEM}"
    mkdir -p "${OUTPUT_DIR}"

    eval "${SD_SCRIPTS_ROOT}/venv/bin/python" \
        "${SD_SCRIPTS_ROOT}/sdxl_gen_img.py" \
        --ckpt "${FILENAME}" \
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
        --from_file "${OUTPUT_DIR_ROOT}/prompts.txt" \
        "${ARG_LORA}"

done
