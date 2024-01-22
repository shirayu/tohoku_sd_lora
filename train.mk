
all:
	:

OUT_DIR:=/please/designate
BASE_MODEL:=~/data/sd/models/_base/animagine-xl-3.0-base.safetensors
BASIC_RESO=1024
MAX_RESO=1568
LR=4e-6
LR_SCHEDULER=cosine
OPTIMIZER="Lion"
BS=12
# DIM>0 => LoRA
DIM=0
EPOCH=10

###-------------
AUTO_TAG_TILE:=./data/auto_tags.jsonl
DIR_IMG_SRC:=./data/img/train_1024
DIR_IMAGES_for_style:=./data/img/train_1024_filtered_for_style

mksymlink_for_style:
	python ./scripts/filtered_mksymlink.py \
		--ex ./data/exclude_images.tsv \
		-i $(DIR_IMG_SRC) \
		-o $(DIR_IMAGES_for_style) 

META1_for_style:=$(DIR_IMAGES_for_style).meta_1.json
meta_1_for_style:
	python ./scripts/generate_meta1.py \
	    --tag $(AUTO_TAG_TILE) \
	    --tag-target ./data/tag_target.json \
	    -i $(DIR_IMAGES_for_style) \
	    -o $(META1_for_style)


train:
	rm -f $(OUT_DIR)/base.safetensors
	ln -s $(BASE_MODEL) $(OUT_DIR)/base.safetensors
	DIM=$(DIM) bash ./step_4_train.sh \
		$(OUT_DIR) \
		$(OUTPUT_MODEL_DIR) \
	    "--float optimizer.learning_rate=$(LR) --str optimizer.lr_scheduler=$(LR_SCHEDULER) --str optimizer.optimizer_type=$(OPTIMIZER) --int training.max_train_epochs=$(EPOCH) --int training.gradient_accumulation_steps=1" \
	    "--int datasets.batch_size=$(BS)"


SHELL=/bin/bash
.DELETE_ON_ERROR:
