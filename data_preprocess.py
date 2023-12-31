import argparse
import pickle
from tqdm import tqdm
from collections import defaultdict

from transformers import BertTokenizer
from tokenizers import normalizers
from tokenizers.normalizers import NFD, NFKD, NFC, NFKC, Lowercase, StripAccents, Strip, Replace, BertNormalizer


def construct_parallel_data_para(src_path, trg_path):
    parallel_data = []

    with open(src_path, "r") as f:
        src_lines = f.readlines()
    with open(trg_path, "r") as f:
        trg_lines = f.readlines()

    assert len(src_lines) == len(trg_lines)
    print("data size: " + str(len(src_lines)))

    c_no_error_sent = 0

    for src_line, trg_line in zip(src_lines, trg_lines):
        src_items = src_line.strip().split("\t")
        assert len(src_items) == 2
        src_sent = src_items[1]
        trg_items = trg_line.strip().split("\t")
        assert trg_items[0] == src_items[0]
        id = trg_items[0]
        trg_sent = trg_items[1]
        modification = []
        if src_sent == trg_sent:
            c_no_error_sent += 1
        else:
            for i, (src_char, trg_char) in enumerate(zip(src_sent, trg_sent)):
                if src_char != trg_char:
                    modification.append((i, trg_char))
        parallel_data.append((id, src_sent, trg_sent, modification))
    print("error-free sentences: " + str(c_no_error_sent))

    return parallel_data


def encode_parallel_data(config, parallel_data, normalizer, tokenizer, max_len, ids2pinyin):
    data = []
    for item in tqdm(parallel_data):
        data_sample = {}
        if config.normalize == "True":
            src_norm = normalizer.normalize_str(item[1])[:max_len - 2]
            trg_norm = normalizer.normalize_str(item[2])[:max_len - 2]
        else:
            src_norm = item[1][:max_len - 2]
            trg_norm = item[2][:max_len - 2]

        if len(src_norm) != len(trg_norm):
            pass

        src_token_list = list(src_norm)
        trg_token_list = list(trg_norm)
        src_token_list.insert(0, '[CLS]')
        src_token_list.append('[SEP]')
        trg_token_list.insert(0, '[CLS]')
        trg_token_list.append('[SEP]')
        data_sample['id'] = item[0]
        data_sample['src_text'] = item[1]
        data_sample['input_ids'] = tokenizer.convert_tokens_to_ids(src_token_list)
        data_sample['token_type_ids'] = [0 for _ in range(len(src_token_list))]
        data_sample['attention_mask'] = [1 for _ in range(len(src_token_list))]
        data_sample['pinyin_ids'] = [ids2pinyin[i] for i in data_sample['input_ids']]
        data_sample['trg_ids'] = tokenizer.convert_tokens_to_ids(trg_token_list)
        data_sample['trg_text'] = item[2]

        data_sample['modification'] = item[3]

        data.append(data_sample)

    return data


def construct_parallel_data_lbl(src_path, trg_path):
    parallel_data = []

    with open(src_path, "r") as f:
        src_lines = f.readlines()
    with open(trg_path, "r") as f:
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

        parallel_data.append((id, src_sent, trg_sent, modification))

    print("error-free sentences: " + str(c_no_error_sent))

    return parallel_data


def encode_predict_data(config, src_path, normalizer, tokenizer, max_len, ids2pinyin):
    data = []

    with open(src_path, "r") as f:
        src_lines = f.readlines()

    print("data size: " + str(len(src_lines)))

    for src_line in src_lines:
        data_sample = {}
        src_items = src_line.strip().split("\t")
        assert len(src_items) == 2
        src_sent = src_items[1]
        id = src_items[0]

        if config.normalize == "True":
            src_norm = normalizer.normalize_str(src_sent)[:max_len - 2]
        else:
            src_norm = normalizer.normalize_str(src_sent)[:max_len - 2]

        src_token_list = list(src_norm)
        src_token_list.insert(0, '[CLS]')
        src_token_list.append('[SEP]')
        data_sample['id'] = id
        data_sample['src_text'] = src_sent
        data_sample['input_ids'] = tokenizer.convert_tokens_to_ids(src_token_list)
        data_sample['token_type_ids'] = [0 for i in range(len(src_token_list))]
        data_sample['attention_mask'] = [1 for i in range(len(src_token_list))]
        data_sample['pinyin_ids'] = [ids2pinyin[i] for i in data_sample['input_ids']]
        data.append(data_sample)

    return data


def save_as_pkl(data, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def main(config):
    print(config.__dict__)
    tokenizer = BertTokenizer.from_pretrained(config.bert_path)

    ids2pinyin = defaultdict(int)
    with open("pymodel/vocab/pinyin_mapping.txt") as f:
        for l in f:
            ids, pinyin = l.strip().split()
            ids2pinyin[int(ids)] = int(pinyin)

    do_zimu = False
    if do_zimu:
        ZM2ID = {':': 1, 'a': 2, 'c': 3, 'b': 4, 'e': 5, 'd': 6, 'g': 7, 'f': 8, 'i': 9, 'h': 10, 'k': 11, 'j': 12,
                 'm': 13, 'l': 14, 'o': 15, 'n': 16, 'q': 17, 'p': 18, 's': 19, 'r': 20, 'u': 21, 't': 22, 'w': 23,
                 'v': 24, 'y': 25, 'x': 26, 'z': 27}
        PYLEN = 5
        ids2zimu = defaultdict(int)
        f = open('pymodel/vocab/pinyin_vocab.txt')
        lines = f.readlines()
        for k in ids2pinyin:
            pinyin = lines[ids2pinyin[k]].strip()
            if pinyin != '[OTHER]':
                seq = []
                for c in pinyin:
                    seq.append(ZM2ID[c])
                seq = [0] * PYLEN + seq
                seq = seq[-PYLEN:]
                ids2zimu[k] = seq
            else:
                ids2zimu[k] = [0] * PYLEN

    normalizer = normalizers.Sequence([Lowercase()])
    if config.target_dir:
        if config.data_mode == "para":
            parallel_data = construct_parallel_data_para(config.source_dir, config.target_dir)
        elif config.data_mode == "lbl":
            parallel_data = construct_parallel_data_lbl(config.source_dir, config.target_dir)
        else:
            print("Wrong data mode!")
            exit()

        encode_data = encode_parallel_data(config, parallel_data, normalizer, tokenizer, config.max_len, ids2pinyin)
        save_as_pkl(encode_data, config.save_path)
    else:
        encode_data = encode_predict_data(config, config.source_dir, normalizer, tokenizer, config.max_len, ids2pinyin)
        save_as_pkl(encode_data, config.save_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_dir", required=True, type=str)
    parser.add_argument("--target_dir", type=str)
    parser.add_argument("--bert_path", default="bert-base-chinese", type=str)
    parser.add_argument("--max_len", default=128, type=int)
    parser.add_argument("--save_path", required=True, type=str)
    parser.add_argument("--data_mode", required=True, type=str)
    parser.add_argument("--normalize", default="True", type=str)
    args = parser.parse_args()
    main(args)
