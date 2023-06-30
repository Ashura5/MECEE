DATA_DIR=data
TEST_SRC_FILE=data/test.txt
TEST_SRC_Fluent_FILE=data/test_1.src
TAG=test
SAVE_PATH=data/model_intergration
model4_file=data/train_val/test_res.txt
mkdir -p $SAVE_PATH

python model_integration.py \
    --output1 $SAVE_PATH"/"$TAG".txt"\
    --output2 $SAVE_PATH"/"$TAG"_res.txt"\
    --output3 $SAVE_PATH"/"$TAG".lbl"\
    --model4_file $model4_file \
    --error_file $TEST_SRC_FILE \
    --threshold 3 \
    --correct_files $DATA_DIR"/test_2021/"$TAG"_res.txt" $DATA_DIR"/test_2022/"$TAG"_res.txt" $DATA_DIR"/test_2023/"$TAG"_res.txt" $DATA_DIR"/test_2024/"$TAG"_res.txt" $DATA_DIR"/test_old_2021/"$TAG"_res.txt" $DATA_DIR"/test_old_2022/"$TAG"_res.txt"

python fluent/fluent.py \
    --src_path $TEST_SRC_Fluent_FILE \
    --hyp_path $SAVE_PATH"/"$TAG".lbl" \
    --out_path $SAVE_PATH"/"$TAG"_fluent.lbl"

python save_parallel_data.py \
    --input_src $TEST_SRC_Fluent_FILE \
    --input_lbl $SAVE_PATH"/"$TAG"_fluent.lbl"  \
    --output1 $SAVE_PATH"/"$TAG"_fluent.txt" \
    --output2 $SAVE_PATH"/"$TAG"_fluent_res.txt"

