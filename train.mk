
all:
	:

SHELL=/bin/bash
.DELETE_ON_ERROR:

DIR_SD_SCRIPTS:=~/workspace/sd-scripts
PYTHON=$(DIR_SD_SCRIPTS)/venv/bin/python

OUT_DIR:=./tmp/out
BASE_MODEL:=~/data/sd/models/_base/animagine-xl-3.0-base.safetensors
BASE_MODEL_FILE_FOR_GEN_TEST:=$(BASE_MODEL)
BASIC_RESO=1024
MAX_RESO=1568
LR=1e-4
LR_SCHEDULER=constant
OPTIMIZER="Lion"
BS=15
NUM_REPEATS=12
# DIM>0 => LoRA
DIM:=8
DIM_FOR_STYLE:=$(DIM)
DIM_FOR_CHARA:=$(DIM)
EPOCH=10
MIXED_PRECISION=bf16
FULL_BF16:=True
FP8:=True
ARG_TRAIN_LEARNING_PRAM:=--float optimizer.learning_rate=$(LR) --str optimizer.lr_scheduler=$(LR_SCHEDULER) --str optimizer.optimizer_type=$(OPTIMIZER) --int training.max_train_epochs=$(EPOCH) --int training.gradient_accumulation_steps=1 --bool training.fp8_base=$(FP8) --bool training.full_bf16=$(FULL_BF16) --int save.save_every_n_epochs=999
ARG_TRAIN_DATASET_PARAM:=--int datasets.batch_size=$(BS) --int datasets.num_repeats=$(NUM_REPEATS)

###-------------
AUTO_TAG_TILE:=./data/auto_tags.jsonl
TRIGGER_FILE:=./data/trigger.json
TAG_GROUPS_DIR:=./data/tag_groups
DIR_IMG_SRC:=./data/img/train_1024
TEST_PROMPT_TEMPLATE:=./data/config/test_prompt_template.txt
TEST_PROMPT_POSITIVE:=./data/config/test_prompt_common_positive.txt
TEST_PROMPT_NEGATIVE:=./data/config/test_prompt_common_negative.txt

###-------------
DIR_ROOT_STYLE:=$(OUT_DIR)/style
DIR_IMAGES_for_style:=$(DIR_ROOT_STYLE)/images
META1_for_style:=$(DIR_ROOT_STYLE)/meta_1.json
META2_for_style:=$(DIR_ROOT_STYLE)/meta_2.json
META3_for_style:=$(DIR_ROOT_STYLE)/meta_3.json
DIR_STYLE_MODEL:=$(DIR_ROOT_STYLE)/model
MY_STYLE_LORA_FILE:=$(DIR_STYLE_MODEL)/mymodel.safetensors
MY_STYLE_PROMPT_CONFIG_FILE:=$(DIR_STYLE_MODEL)/config/prompt_config.json
MY_STYLE_TEST_GEN_DIR:=$(DIR_STYLE_MODEL)/gen_test
MY_STYLE_TEST_GEN_PROMPT:=$(MY_STYLE_TEST_GEN_DIR)/prompots.txt

mksymlink_for_style:
	python ./scripts/train_lora/filtered_mksymlink.py \
		--ex ./data/exclude_images.tsv \
		-i $(DIR_IMG_SRC) \
		-o $(DIR_IMAGES_for_style) \
	    	--for_style

meta_1_for_style:
	poetry run python ./scripts/train_lora/generate_meta1.py \
	    --tag $(AUTO_TAG_TILE) \
	    --tag-group $(TAG_GROUPS_DIR) \
	    --tag-trigger $(TRIGGER_FILE) \
	    -i $(DIR_IMAGES_for_style) \
	    -o $(META1_for_style) \
	    --for_style

meta_2_for_style:
	$(PYTHON) $(DIR_SD_SCRIPTS)/finetune/prepare_buckets_latents.py \
	    $(DIR_IMAGES_for_style) \
	    $(META1_for_style) \
	    $(META2_for_style) \
	    $(BASE_MODEL) \
	    --mixed_precision $(MIXED_PRECISION) \
	    --min_bucket_reso 512 \
	    --max_resolution "$(BASIC_RESO),$(BASIC_RESO)" \
	    --max_bucket_reso $(MAX_RESO) \
	    --batch_size 4

prepare_for_style: \
	mksymlink_for_style \
	meta_1_for_style \
	meta_2_for_style

MY_STYLE_TEST_GEN_DONE:=$(DIR_ROOT_STYLE)/done
$(MY_STYLE_LORA_FILE):
	rm -f $(DIR_ROOT_STYLE)/base.safetensors
	ln -s $(BASE_MODEL) $(DIR_ROOT_STYLE)/base.safetensors
	cp $(META2_for_style) $(META3_for_style)
	DIM=$(DIM_FOR_STYLE) \
	   bash \
		./scripts/train_lora/train_lora.sh \
		$(DIR_ROOT_STYLE) \
		$(DIR_STYLE_MODEL) \
	    "${ARG_TRAIN_LEARNING_PRAM}" \
	    "${ARG_TRAIN_DATASET_PARAM}"
train_for_style: $(MY_STYLE_LORA_FILE) $(MY_STYLE_TEST_GEN_DONE)

train_for_style_tensorboard:
	poetry run tensorboard --logdir $(DIR_STYLE_MODEL)/log --bind_all

$(MY_STYLE_PROMPT_CONFIG_FILE):
	mkdir -p $(dir $@)
	python ./scripts/train_lora/meta3_to_prompt_config.py -i $(DIRNAME2TRIGGER) --key oistyle -o $@

$(MY_STYLE_TEST_GEN_PROMPT): $(MY_STYLE_PROMPT_CONFIG_FILE)
	mkdir -p $(dir $@)
	python ./scripts/train_lora/convert_test_prompt.py \
	    -i $(TEST_PROMPT_TEMPLATE) \
	    --positive $(TEST_PROMPT_POSITIVE) \
	    --negative $(TEST_PROMPT_NEGATIVE) \
	    -o $@ \
	    --config $< 

gen_test_imgs_for_style: $(MY_STYLE_TEST_GEN_DONE)
$(MY_STYLE_TEST_GEN_DONE): $(BASE_MODEL_FILE_FOR_GEN_TEST) $(MY_STYLE_TEST_GEN_PROMPT) $(MY_STYLE_LORA_FILE) $(MY_STYLE_ROOT_DIR)
	bash -x ./scripts/gen_img.sh \
	    $(BASE_MODEL_FILE_FOR_GEN_TEST) \
	    $(MY_STYLE_TEST_GEN_PROMPT) \
	    $(MY_STYLE_TEST_GEN_DIR) \
	    $(MY_STYLE_LORA_FILE) \
	&& touch $@

STYLE_MERGED_MODEL:=$(OUT_DIR)/base.style_merged.safetensors
style_merge: $(STYLE_MERGED_MODEL)
MERGE_PRECISION:=fp16
$(STYLE_MERGED_MODEL):
	$(PYTHON) $(DIR_SD_SCRIPTS)/networks/sdxl_merge_lora.py \
	--sd_model $(BASE_MODEL) \
	--models $(DIR_STYLE_MODEL)/mymodel.safetensors \
	--precision $(MERGE_PRECISION) \
	--save_precision $(MERGE_PRECISION) \
	--save_to $(STYLE_MERGED_MODEL) \
	--ratios 1.0


###-------------

CHARA_WITHOUT_STYLE:=0
ifeq ($(CHARA_WITHOUT_STYLE),0)
	GENERATE_META1_ARG:=--no_style_trigger_word
	DIR_ROOT_CHARA:=$(OUT_DIR)/chara_with_style
else
	BASE_MODEL:=$(STYLE_MERGED_MODEL)
	DIR_ROOT_CHARA:=$(OUT_DIR)/chara_without_style
endif
DIR_IMAGES_for_chara:=$(DIR_ROOT_CHARA)/images
META1_for_chara:=$(DIR_ROOT_CHARA)/meta_1.json
DIRNAME2TRIGGER:=$(DIR_ROOT_CHARA)/dirname2trigger.json
META2_for_chara:=$(DIR_ROOT_CHARA)/meta_2.json
META3_DIR_for_chara:=$(DIR_ROOT_CHARA)/meta_3/
DIR_CHARA_MODEL:=$(DIR_ROOT_CHARA)/model
BASE_MODEL_FILE:=$(DIR_ROOT_CHARA)/base.safetensors

mksymlink_for_chara:
	rm -rf $(DIR_IMAGES_for_chara)
	python ./scripts/train_lora/filtered_mksymlink.py \
		--ex ./data/exclude_images.tsv \
		-i $(DIR_IMG_SRC) \
		-o $(DIR_IMAGES_for_chara) \

meta_1_for_chara:
	poetry run python ./scripts/train_lora/generate_meta1.py \
	    --tag $(AUTO_TAG_TILE) \
	    --tag-group $(TAG_GROUPS_DIR) \
	    --tag-trigger $(TRIGGER_FILE) \
	    -i $(DIR_IMAGES_for_chara) \
	    -o $(META1_for_chara) \
	    --output_triggers $(DIRNAME2TRIGGER) \
	    $(GENERATE_META1_ARG)

meta_2_for_chara:
	$(PYTHON) $(DIR_SD_SCRIPTS)/finetune/prepare_buckets_latents.py \
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
	python ./scripts/train_lora/generate_meta3.py \
		-i $(META2_for_chara) \
		-o $(META3_DIR_for_chara)

prepare_for_chara: \
	mksymlink_for_chara \
	meta_1_for_chara \
	meta_2_for_chara \
	meta_3_for_chara


###-------------
META3:=/please/designate
META3NAME:=$(shell basename $(META3) .json)
MY_CHARA_ROOT_DIR:=$(DIR_CHARA_MODEL)/$(META3NAME)
PROMPT_CONFIG_FILE:=$(MY_CHARA_ROOT_DIR)/config/prompt_config.json
MY_CHARA_LORA_FILE:=$(MY_CHARA_ROOT_DIR)/mymodel.safetensors
MY_CHARA_TEST_GEN_DIR:=$(MY_CHARA_ROOT_DIR)/gen_test
MY_CHARA_TEST_GEN_PROMPT:=$(MY_CHARA_TEST_GEN_DIR)/prompots.txt
MY_CHARA_TEST_GEN_DONE:=$(MY_CHARA_TEST_GEN_DIR)/done

$(MY_CHARA_TEST_GEN_PROMPT): $(PROMPT_CONFIG_FILE)
	mkdir -p $(dir $@)
	python ./scripts/train_lora/convert_test_prompt.py \
	    -i $(TEST_PROMPT_TEMPLATE) \
	    --positive $(TEST_PROMPT_POSITIVE) \
	    --negative $(TEST_PROMPT_NEGATIVE) \
	    -o $@ \
	    --config $< 

gen_test_imgs_for_chara: $(MY_CHARA_TEST_GEN_DONE)
$(MY_CHARA_TEST_GEN_DONE): $(BASE_MODEL_FILE_FOR_GEN_TEST) $(MY_CHARA_TEST_GEN_PROMPT) $(MY_CHARA_LORA_FILE) $(MY_CHARA_ROOT_DIR)
	bash -x ./scripts/gen_img.sh \
	    $(BASE_MODEL_FILE_FOR_GEN_TEST) \
	    $(MY_CHARA_TEST_GEN_PROMPT) \
	    $(MY_CHARA_TEST_GEN_DIR) \
	    $(MY_CHARA_LORA_FILE) \
	&& touch $@


train_for_chara: $(MY_CHARA_LORA_FILE) $(PROMPT_CONFIG_FILE) gen_test_imgs_for_chara
$(PROMPT_CONFIG_FILE): $(META3) $(DIRNAME2TRIGGER)
	python ./scripts/train_lora/meta3_to_prompt_config.py -i $(DIRNAME2TRIGGER) --key $(META3NAME) -o $@

$(MY_CHARA_LORA_FILE): $(META3)
	mkdir -p $(MY_CHARA_ROOT_DIR)
	rm -f $(BASE_MODEL_FILE)
	ln -s $(BASE_MODEL) $(BASE_MODEL_FILE)
	test ! -z $(META3)
	META3=$(META3) \
	DIM=$(DIM_FOR_CHARA) \
	    bash \
		./scripts/train_lora/train_lora.sh \
		$(DIR_ROOT_CHARA) \
		$(MY_CHARA_ROOT_DIR) \
	    "${ARG_TRAIN_LEARNING_PRAM}" \
	    "${ARG_TRAIN_DATASET_PARAM}"
	

train_for_chara_tensorboard:
	poetry run tensorboard --logdir $(MY_CHARA_ROOT_DIR)/log --bind_all


