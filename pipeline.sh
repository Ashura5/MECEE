# Step 1. Data preprocessing
DATA_DIR=./exp_data/val_6
PRETRAIN_MODEL=./csc/bert
mkdir -p $DATA_DIR
export CUDA_VISIBLE_DEVICES=0


TRAIN_SRC_FILE=data/train_6.src
TRAIN_TRG_FILE=data/train_6.trg
DEV_SRC_FILE=data/val_1.src
DEV_TRG_FILE=data/val.lbl
TEST_SRC_FILE=data/val_1.src
TEST_TRG_FILE=data/val.lbl

if [ ! -f $DATA_DIR"/train.pkl" ]; then
    python ./data_preprocess.py \
    --source_dir $TRAIN_SRC_FILE \
    --target_dir $TRAIN_TRG_FILE \
    --bert_path $PRETRAIN_MODEL \
    --save_path $DATA_DIR"/train.pkl" \
    --data_mode "para" \
    --normalize "True"
fi

if [ ! -f $DATA_DIR"/dev.pkl" ]; then
    python ./data_preprocess.py \
    --source_dir $DEV_SRC_FILE \
    --target_dir $DEV_TRG_FILE \
    --bert_path $PRETRAIN_MODEL \
    --save_path $DATA_DIR"/dev.pkl" \
    --data_mode "lbl" \
    --normalize "True"
fi

if [ ! -f $DATA_DIR"/test.pkl" ]; then
    python ./data_preprocess.py \
    --source_dir $TEST_SRC_FILE \
    --target_dir $TEST_TRG_FILE \
    --bert_path $PRETRAIN_MODEL \
    --save_path $DATA_DIR"/test.pkl" \
    --data_mode "lbl" \
    --normalize "True"
fi


# Step 2. Training
MODEL_DIR=./exps/val_old_2023
CUDA_DEVICE=0
mkdir -p $MODEL_DIR/bak
cp ./pipeline.sh $MODEL_DIR/bak

CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python -u train_pipeline.py \
    --pretrained_model $PRETRAIN_MODEL \
    --train_path $DATA_DIR"/train.pkl" \
    --dev_path $DATA_DIR"/dev.pkl" \
    --test_path $DATA_DIR"/test.pkl" \
    --lbl_path $DEV_TRG_FILE \
    --test_lbl_path $TEST_TRG_FILE \
    --save_path $MODEL_DIR \
    --batch_size 64 \
    --num_epochs 3 \
    --lr 5e-5 \
    --tie_cls_weight False \
    --tag "val_6" \
    --seed 2023 \
    2>&1 | tee $MODEL_DIR"/log.txt"


# prediction
