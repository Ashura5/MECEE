import argparse
from collections import Counter
from itertools import zip_longest
import sys

def correct_sentences_from_files(error_file, correct_files, weights, threshold):
    correct_sentences = [open(file, "r", encoding="utf-8").read().split('\n') for file in correct_files]
    error_sentences = open(error_file, "r", encoding="utf-8").read().split('\n')
    corrected_sentences = []

    for sentences in zip_longest(error_sentences, *correct_sentences):
        error_sentence = sentences[0]
        correct_sentences = sentences[1:]
        counters = [Counter() for _ in range(len(error_sentence))]

        for sentence, weight in zip(correct_sentences, weights):
            for i, char in enumerate(sentence):
                if char != error_sentence[i]:
                    counters[i][char] += weight

        new_sentence = ""
        for i, counter in enumerate(counters):
            if counter:
                most_common_char, weight = counter.most_common(1)[0]
                if weight > threshold:
                    new_sentence += most_common_char
                else:
                    new_sentence += error_sentence[i]
            else:
                new_sentence += error_sentence[i]

        corrected_sentences.append(new_sentence)

    return corrected_sentences


def correct_sentence(error_sentence, correct_sentences):
    new_sentence = list(error_sentence)  # 将错误句子转为字符列表方便后续操作

    for i in range(len(new_sentence)):  # 对于错误句子中的每个字符
        for sentence in correct_sentences:  # 遍历每个修正后的句子
            if len(sentence) > i and sentence[i] != new_sentence[i]:  # 如果该字符有修改
                new_sentence[i] = sentence[i]  # 使用修改后的字符
                break  # 跳出内层循环，只保留第一个修改

    return ''.join(new_sentence)  # 将字符列表重新拼接为字符串并返回


def process_files(error_filename, correct_filenames, output_filename):
    with open(error_filename, 'r', encoding='utf-8') as error_file:
        error_sentences = error_file.read().splitlines()

    correct_sentences_list = []
    for filename in correct_filenames:
        with open(filename, 'r', encoding='utf-8') as file:
            correct_sentences_list.append(file.read().splitlines())

    with open(output_filename, 'w', encoding='utf-8') as output_file:
        for i in range(len(error_sentences)):
            correct_sentences = [sentences[i] for sentences in correct_sentences_list]
            output_sentence = correct_sentence(error_sentences[i], correct_sentences)
            output_file.write(output_sentence + '\n')

def construct_trg_file(src_path, parallel_path, trg_path):
    with open(src_path, "r", encoding="utf-8") as f:
        src_lines = f.readlines()
    with open(parallel_path, "r", encoding="utf-8") as f:
        parallel_data = f.readlines()
    assert len(src_lines) == len(parallel_data)
    print("data size: " + str(len(src_lines)))

    with open(trg_path, "w", encoding="utf-8") as f:
        j=0
        for src_line,trg_sent in zip(src_lines, parallel_data):
            src_items = src_line.strip()
            trg_sent=trg_sent.strip()
            src_sent = src_items
            trg_items = []
            modification = []
            assert len(src_sent)==len(trg_sent)
            for i in range(len(src_sent)):
                if src_sent[i] != trg_sent[i]:
                    trg_items.append(str(i + 1))
                    trg_items.append(trg_sent[i])
                    modification.append((i, trg_sent[i]))
            trg_line ="CSC_test_"+str(j)+", "+ ", ".join(trg_items)
            if len(trg_items) == 0:
                trg_line = trg_line + "0"
            f.write(trg_line + "\n")
            j=j+1

    print("The target file is successfully created.")

def main(args):
    if args.weights is None:
        args.weights = [1] * len(args.correct_files)
    elif len(args.weights) != len(args.correct_files):
        print("Error: The number of weights does not match the number of correct files.")
        sys.exit(1)

    corrected_sentences=correct_sentences_from_files(args.error_file, args.correct_files, args.weights, args.threshold)
    with open(args.output1, 'w', encoding="utf-8") as fp:
        [fp.write(str(corrected) + '\n') for corrected in corrected_sentences[:-1]]
        fp.close()
    process_files(args.error_file, [args.output1,args.model4_file], args.output2)
    construct_trg_file(args.error_file, args.output2,args.output3)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output1", required=True, type=str, help="Output file path")
    parser.add_argument("--output2", required=True, type=str, help="Output file path")
    parser.add_argument("--output3", required=True, type=str, help="Output file path")
    parser.add_argument("--model4_file", required=True, type=str, help="output of model4")
    parser.add_argument("--error_file", required=True, type=str, help="Error file path")
    parser.add_argument("--correct_files", nargs='+', required=True, help="List of correct files")
    parser.add_argument("--weights", nargs='+', type=float, help="Weights for each correct file")
    parser.add_argument("--threshold", default=None, type=float, help="Threshold for correction")


    args = parser.parse_args()
    if args.threshold is None:
        args.threshold = len(args.correct_files) / 2

    main(args)
