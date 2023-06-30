import argparse
import jieba
import time
from models import MaskedBert
from tqdm import tqdm
def read_data(path, src):
    data = []
    with open(path, "r", encoding="utf8") as fin:
        lines = fin.readlines()
    for line, src_line in zip(lines, src):
        src_list = list(src_line)
        sent = src_line
        items = line.strip().split(", ")
        if len(items) == 2:
            pass
        else:
            for i in range(1, len(items), 2):
                src_list[int(items[i]) - 1] = items[i + 1]
            sent = ''.join(src_list)
        data.append(sent)
    return data


def read_src(path):
    data = []
    with open(path, "r", encoding="utf8") as fin:
        lines = fin.readlines()
    for line in lines:
        items = line.strip().split("\t")
        data.append(items[1])
    return data


def main(args):
    start_time = time.time()

    model = MaskedBert.from_pretrained("./fluent/chinese_bert_wwm_ext_pytorch", sentence_length=100)

    print(f"Loading ngrams model cost {time.time() - start_time:.3f} seconds.")

    src = read_src(args.src_path)
    pred_data = read_data(args.hyp_path, src)

    count = 0
    n = 0
    boost = []
    threshold = 0.3

    f1 = open(args.hyp_path, encoding="utf8")
    lines = f1.readlines()

    f2 = open(args.out_path, "w", encoding="utf8")
    for s1, s2, line in tqdm(zip(src, pred_data, lines)):
        ppl1 = model.perplexity(x=jieba.lcut(s1), verbose=False)
        ppl2 = model.perplexity(x=jieba.lcut(s2), verbose=False)

        if s2 != s1 and ppl2 - ppl1 > threshold:
            print('不纠')
            print(s1, ppl1)
            print(s2, ppl2)

            id = line.split()[0]
            f2.write(id + ' ' + '0' + '\n')
        else:
            f2.write(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_path", default="data/test_1.src", type=str, help="Source path")
    parser.add_argument("--hyp_path", default="data_f/lixiang-GGbond-ECNU-ResultSubmission052903.lbl", type=str, help="Hypothesis path")
    parser.add_argument("--out_path", default="data_f/decode_f/lixiang-GGbond-ECNU-ResultSubmission052903.lbl", type=str, help="Output path")

    args = parser.parse_args()
    main(args)
