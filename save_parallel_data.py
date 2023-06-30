import argparse

def construct_parallel_data_lbl(src_path, trg_path):
    parallel_data = []

    with open(src_path, "r", encoding="utf-8") as f:
        src_lines = f.readlines()
    with open(trg_path, "r", encoding="utf-8") as f:
        trg_lines = f.readlines()

    assert len(src_lines) == len(trg_lines)
    print("data size: " + str(len(src_lines)))

    c_no_error_sent = 0
    for src_line, trg_line in zip(src_lines, trg_lines):
        src_items = src_line.strip().split("\t")
        assert len(src_items) == 2
        src_sent = src_items[1]
        trg_items = trg_line.strip().split(", ")
        id = trg_items[0]
        trg_sent = list(src_sent)
        modification = []
        if len(trg_items) == 2:
            c_no_error_sent += 1
        else:
            for i in range(1, len(trg_items), 2):
                trg_sent[int(trg_items[i]) - 1] = trg_items[i + 1]
                modification.append((int(trg_items[i]) - 1, trg_items[i + 1]))
        trg_sent = "".join(trg_sent)

        parallel_data.append((src_sent, trg_sent))

    print("error-free sentences: " + str(c_no_error_sent))

    return parallel_data
def char_D(sentences):
    total = 0  # 总的句子数
    cor = 0  # 正确识别错误的句子数
    al_wro = 0  # 算法识别为“有错误”的句子数
    wro = 0  # 语料中所有错误句子数
    k = 0
    for sentence in sentences:
        k += 1
        total += 1
        lines0 = sentence[0]
        lines1 = sentence[1]
        lines2 = sentence[2]
        if len(lines0) != len(lines1) or len(lines1) != len(lines2):
            print(f"文本长度不一致")
            print(sentence)
        lines_list = [[lines0[i], lines1[i], lines2[i]] for i in range(min(len(lines0), len(lines1), len(lines2)))]
        for char_list in lines_list:
            if char_list[0] != char_list[1] and char_list[0] != char_list[2]:
                cor += 1
            if char_list[0] != char_list[1]:
                wro += 1
            if char_list[0] != char_list[2]:
                al_wro += 1

    try:
        precision = round((cor / al_wro) * 100, 2)
    except:
        precision = "-"
    try:
        recall = round((cor / wro) * 100, 2)
    except:
        recall = "-"
    try:
        f1 = round(precision * recall * 2 / (precision + recall), 2)
    except:
        f1 = "-"

    print(f"char_detect_precision：{precision}({cor}/{al_wro})")
    print(f"char_detect_recall：{recall}({cor}/{wro})")
    print(f"char_detect_F1：{f1}")



def char_C(sentences):
    total = 0  # 总的句子数
    TP = 0  # 正确识别错误的句子数
    FP = 0  # 非错别字被误报为错别字
    FN = 0  # 错别字未能正确识别错别字
    k = 0
    for sentence in sentences:
        k += 1
        total += 1
        lines0 = sentence[0]
        lines1 = sentence[1]
        lines2 = sentence[2]
        lines_list = [[lines0[i], lines1[i], lines2[i]] for i in range(min(len(lines0), len(lines1), len(lines2)))]
        for char_list in lines_list:
            if char_list[0] != char_list[1] and char_list[1] == char_list[2]:
                TP += 1
            if char_list[2] != char_list[1] and char_list[0] != char_list[2]:
                FP += 1
            if char_list[0] != char_list[1] and char_list[1] != char_list[2]:
                FN += 1

    al_wro = TP + FP
    wro = TP + FN
    cor = TP
    try:
        precision = round((cor / al_wro) * 100, 2)
    except:
        precision = "-"
    try:
        recall = round((cor / wro) * 100, 2)
    except:
        recall = "-"
    try:
        f1 = round(precision * recall * 2 / (precision + recall), 2)
    except:
        f1 = "-"
    print(f"char_correct_precision：{precision}({cor}/{al_wro})")
    print(f"char_correct_recall：{recall}({cor}/{wro})")
    print(f"char_correct_F1：{f1}")



def sentence_FPR(sentences):
    all_num = 0
    cuo = 0
    for sentence in sentences:
        if sentence[0] == sentence[1]:
            all_num += 1
            if sentence[0] != sentence[2]:
                cuo += 1
    if all_num == 0:
        fpr = "-"
    else:
        fpr = f"{cuo/all_num*100:.2f}({cuo}/{all_num})"
    print(f"sentence_FPR：{fpr}")


def test(gold_file,predict_file):
    sents = {}
    flag = False  # 是否有句子异常
    with open(gold_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            lines = line.replace("\n", '').split("\t")
            if "原文" in lines[0] and i == 0:
                continue
            sents[lines[0]] = [lines[0], lines[1]]
    with open(predict_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            lines = line.replace("\n", '').split("\t")
            if "原文" in lines[0] and i == 0:
                continue
            if len(lines[0]) != len(lines[1]):
                flag = True
                print(f"Input and Output have different lengths. Input is {lines[0]}")
                break
            try:
                sents[lines[0]].append(lines[1])
            except:
                flag = True
                print(len(lines),lines[0],lines[1])
                print(f"Can't find the gold, maybe the input is wrong. Input is {lines[0]}")
                break
    if not flag:
        sentences = []
        for value in sents.values():
            if len(value) < 3:
                sentences.append([value[0], value[1], value[0]])
            else:
                sentences.append([value[0], value[1], value[2]])

        sentence_FPR(sentences)
        char_D(sentences)
        char_C(sentences)

def get_res(input_src, input_lbl, output1, output2):
    parallel_data=construct_parallel_data_lbl(input_src,input_lbl)
    with open(output1,'w', encoding="utf-8") as fp:
        [fp.write(str(item[0])+'\t'+str(item[1])+'\n') for item in parallel_data]
    with open(output2,'w', encoding="utf-8") as fp:
        [fp.write(str(item[1])+'\n') for item in parallel_data]

def main(args):
    get_res(args.input_src, args.input_lbl, args.output1, args.output2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_src", default="./test_1.src", type=str, help="Input source path")
    parser.add_argument("--input_lbl", default="./test.lbl", type=str, help="Input label path")
    parser.add_argument("--output1", default="./output/test.txt", type=str, help="Output file 1 path")
    parser.add_argument("--output2", default="./output/test_res.txt", type=str, help="Output file 2 path")

    args = parser.parse_args()
    main(args)
