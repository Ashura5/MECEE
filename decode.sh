PRETRAIN_MODEL=csc/bert
DATA_DIR=data
TEST_SRC_FILE=data/test_1.src
TAG=test

python ./data_preprocess.py \
--source_dir $TEST_SRC_FILE \
--bert_path $PRETRAIN_MODEL \
--save_path $DATA_DIR"/test_"$TAG".pkl" \
--data_mode "lbl" \
--normalize "True"

#MODEL_PATH=/home/lixiang/Spell/exps/test_new_Aug/test_new_Aug3.pt
#MODEL_PATH=/home/lixiang/Spell/exps/train_val/val_69.pt
#MODEL_PATH=/home/lixiang/Spell/exps/val_2021/val_62.pt
#MODEL_PATH=/home/lixiang/Spell/exps/val_2022/val_62.pt
#MODEL_PATH=/home/lixiang/Spell/exps/val_2023/val_63.pt
#MODEL_PATH=/home/lixiang/Spell/exps/val_2024/val_62.pt
#MODEL_PATH=/home/lixiang/Spell/exps/val_old_2021/test_new_61.pt
MODEL_PATH=/home/lixiang/Spell/exps/val_old_2022/val_61.pt
#SAVE_PATH=data/test_new_Aug
#SAVE_PATH=data/test_old_2022
#SAVE_PATH=data/val_2021
#SAVE_PATH=data/val_2022
#SAVE_PATH=data/val_2023
#SAVE_PATH=data/val_2024
#SAVE_PATH=data/test_old_2021
SAVE_PATH=data/test_old_2022

mkdir -p $SAVE_PATH

CUDA_VISIBLE_DEVICES=0 python decode.py \
    --pretrained_model $PRETRAIN_MODEL \
    --test_path $DATA_DIR"/test_"$TAG".pkl" \
    --model_path $MODEL_PATH \
    --save_path $SAVE_PATH"/"$TAG".lbl" ;

python save_parallel_data.py \
    --input_src $TEST_SRC_FILE \
    --input_lbl $SAVE_PATH"/"$TAG".lbl" \
    --output1 $SAVE_PATH"/"$TAG".txt" \
    --output2 $SAVE_PATH"/"$TAG"_res.txt"

