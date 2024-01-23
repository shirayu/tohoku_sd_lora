
all:
	:

OUT_DIR:=./tmp/out
BASE_MODEL:=~/data/sd/models/_base/animagine-xl-3.0-base.safetensors
BASIC_RESO=1024
MAX_RESO=1568
LR=4e-6
LR_SCHEDULER=cosine
OPTIMIZER="Lion"
BS=12
# DIM>0 => LoRA
DIM:=64
DIM_FOR_STYLE:=$(DIM)
EPOCH=10
MIXED_PRECISION=bf16

###-------------
AUTO_TAG_TILE:=./data/auto_tags.jsonl
TARGET_TAG_FILE:=./data/tag_target.json
DIR_IMG_SRC:=./data/img/train_1024

DIR_ROOT_STYLE:=$(OUT_DIR)/style
DIR_IMAGES_for_style:=$(DIR_ROOT_STYLE)/images
META1_for_style:=$(DIR_ROOT_STYLE)/meta_1.json
META2_for_style:=$(DIR_ROOT_STYLE)/meta_2.json
META3_for_style:=$(DIR_ROOT_STYLE)/meta_3.json
DIR_STYLE_MODEL:=$(DIR_ROOT_STYLE)/model

mksymlink_for_style:
	python ./scripts/filtered_mksymlink.py \
		--ex ./data/exclude_images.tsv \
		-i $(DIR_IMG_SRC) \
		-o $(DIR_IMAGES_for_style) \
	    	--for_style

meta_1_for_style:
	python ./scripts/generate_meta1.py \
	    --tag $(AUTO_TAG_TILE) \
	    --tag-target $(TARGET_TAG_FILE) \
	    -i $(DIR_IMAGES_for_style) \
	    -o $(META1_for_style) \
	    --for_style

meta_2_for_style:
	~/workspace/sd-scripts/venv/bin/python \
	    ~/workspace/sd-scripts/finetune/prepare_buckets_latents.py \
	    $(DIR_IMAGES_for_style) \
	    $(META1_for_style) \
	    $(META2_for_style) \
	    $(BASE_MODEL) \
	    --mixed_precision $(MIXED_PRECISION) \
	    --min_bucket_reso 512 \
	    --max_resolution "$(BASIC_RESO),$(BASIC_RESO)" \
	    --max_bucket_reso $(MAX_RESO) \
	    --batch_size 4

train_for_style:
	rm -f $(OUT_DIR)/base.safetensors
	ln -s $(BASE_MODEL) $(OUT_DIR)/base.safetensors
	cp $(META2_for_style) $(META3_for_style)
	DIM=$(DIM_FOR_STYLE) bash ./train.sh \
		$(DIR_ROOT_STYLE) \
		$(DIR_STYLE_MODEL) \
	    "--float optimizer.learning_rate=$(LR) --str optimizer.lr_scheduler=$(LR_SCHEDULER) --str optimizer.optimizer_type=$(OPTIMIZER) --int training.max_train_epochs=$(EPOCH) --int training.gradient_accumulation_steps=1" \
	    "--int datasets.batch_size=$(BS)"


SHELL=/bin/bash
.DELETE_ON_ERROR:
