
all:
	:

SHELL=/bin/bash
.DELETE_ON_ERROR:

OUT_DIR:=./tmp/out
BASE_MODEL:=~/data/sd/models/_base/animagine-xl-3.0-base.safetensors
BASIC_RESO=1024
MAX_RESO=1568
LR=3e-5
LR_SCHEDULER=constant
OPTIMIZER="Lion"
BS=12
# DIM>0 => LoRA
DIM:=32
DIM_FOR_STYLE:=$(DIM)
DIM_FOR_CHARA:=$(DIM)
EPOCH=10
MIXED_PRECISION=bf16
FP8:="False"

###-------------
AUTO_TAG_TILE:=./data/auto_tags.jsonl
TARGET_TAG_FILE:=./data/tag_target.json
DIR_IMG_SRC:=./data/img/train_1024

###-------------
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
	rm -f $(DIR_ROOT_STYLE)/base.safetensors
	ln -s $(BASE_MODEL) $(DIR_ROOT_STYLE)/base.safetensors
	cp $(META2_for_style) $(META3_for_style)
	DIM=$(DIM_FOR_STYLE) \
	PROMPT_PREFIX="oistyle, " \
	    bash \
	    	./train.sh \
		$(DIR_ROOT_STYLE) \
		$(DIR_STYLE_MODEL) \
	    "--float optimizer.learning_rate=$(LR) --str optimizer.lr_scheduler=$(LR_SCHEDULER) --str optimizer.optimizer_type=$(OPTIMIZER) --int training.max_train_epochs=$(EPOCH) --int training.gradient_accumulation_steps=1" \
	    "--int datasets.batch_size=$(BS)"

train_for_style_tensorboard:
	poetry run tensorboard --logdir $(DIR_STYLE_MODEL)/log


###-------------

DIR_ROOT_CHARA:=$(OUT_DIR)/chara
DIR_IMAGES_for_chara:=$(DIR_ROOT_CHARA)/images
META1_for_chara:=$(DIR_ROOT_CHARA)/meta_1.json
META2_for_chara:=$(DIR_ROOT_CHARA)/meta_2.json
META3_DIR_for_chara:=$(DIR_ROOT_CHARA)/meta_3/
DIR_CHARA_MODEL:=$(DIR_ROOT_CHARA)/model

mksymlink_for_chara:
	rm -rf $(DIR_IMAGES_for_chara)
	python ./scripts/filtered_mksymlink.py \
		--ex ./data/exclude_images.tsv \
		-i $(DIR_IMG_SRC) \
		-o $(DIR_IMAGES_for_chara) \

meta_1_for_chara:
	python ./scripts/generate_meta1.py \
	    --tag $(AUTO_TAG_TILE) \
	    --tag-target $(TARGET_TAG_FILE) \
	    -i $(DIR_IMAGES_for_chara) \
	    -o $(META1_for_chara) \
	    --no_style_trigger_word

meta_2_for_chara:
	~/workspace/sd-scripts/venv/bin/python \
	    ~/workspace/sd-scripts/finetune/prepare_buckets_latents.py \
	    $(DIR_IMAGES_for_chara) \
	    $(META1_for_chara) \
	    $(META2_for_chara) \
	    $(BASE_MODEL) \
	    --mixed_precision $(MIXED_PRECISION) \
	    --min_bucket_reso 512 \
	    --max_resolution "$(BASIC_RESO),$(BASIC_RESO)" \
	    --max_bucket_reso $(MAX_RESO) \
	    --batch_size 4

meta_3_for_chara:
	python ./scripts/generate_meta3.py \
		-i $(META2_for_chara) \
		-o $(META3_DIR_for_chara)

prepare_for_chara: \
	mksymlink_for_chara \
	meta_1_for_chara \
	meta_2_for_chara \
	meta_3_for_chara

META3:=
META3_DIR:=$(DIR_CHARA_MODEL)/$(shell basename $(META3) .json)
train_for_chara:
	mkdir -p $(META3_DIR)
	rm -f $(DIR_ROOT_CHARA)/base.safetensors
	ln -s $(BASE_MODEL) $(DIR_ROOT_CHARA)/base.safetensors
	test ! -z $(META3)
	META3=$(META3) \
	DIM=$(DIM_FOR_CHARA) \
	    bash \
	    	./train.sh \
		$(DIR_ROOT_CHARA) \
		$(META3_DIR) \
	    "--float optimizer.learning_rate=$(LR) --str optimizer.lr_scheduler=$(LR_SCHEDULER) --str optimizer.optimizer_type=$(OPTIMIZER) --int training.max_train_epochs=$(EPOCH) --int training.gradient_accumulation_steps=1 --bool training.fp8_base=$(FP8) --int save.save_every_n_epochs=999 " \
	    "--int datasets.batch_size=$(BS)"

train_for_chara_tensorboard:
	poetry run tensorboard --logdir $(META3_DIR)/log


