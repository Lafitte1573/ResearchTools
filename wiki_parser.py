import json
import os
from os import path
from opencc import OpenCC

import argparse

from tqdm import tqdm
import pandas as pd
import shutil

# 繁体转简体（支持多种模式：t2s, s2twp等）
converter = OpenCC('t2s')
# traditional_text = "這是一個繁體字的範例。"
# simplified_text = converter.convert(traditional_text)
# print(simplified_text)  # 输出：这是一个繁体字的范例。
# # exit()


def wiki_processing():
    # data_path = '/mnt/data/djx/wiki_zh_latest'

    error = 0
    dataset = []
    for _dir in tqdm(os.listdir(args.data_folder)):
        file_path = path.join(args.data_folder, _dir)
        for i, _file in enumerate(os.listdir(file_path)):
            # text = [json.loads(line) for line in open(path.join(file_path, _file), 'r', encoding='utf-8').readlines()]
            try:
                texts = [json.loads(line) for line in open(path.join(file_path, _file), 'r').readlines()]
                for text in texts:
                    text['text'] = converter.convert(text['text'])
                    text['title'] = converter.convert(text['title'])
                # print(i, len(texts), texts[0])
                # print()
                dataset.extend(texts)
            except UnicodeDecodeError as e:
                print(e)
                error += 1
                continue

        if args.remove_input:
            # 删除文件夹及其内容
            shutil.rmtree(file_path)

    # 写入新文件
    if args.format == 'json':
        with open(path.join(args.output_dir, 'wiki_zh_latest.json'), 'w', encoding='utf-8') as f:
            for text in dataset:
                f.write(json.dumps(text, ensure_ascii=False) + '\n')
    elif args.format == 'jsonl':
        with open(path.join(args.output_dir, 'wiki_zh_latest.jsonl'), 'w', encoding='utf-8') as f:
            for text in dataset:
                f.write(json.dumps(text, ensure_ascii=False) + '\n')
    elif args.format == 'parquet':
        # 将数据转换为DataFrame
        df = pd.DataFrame(dataset)
        output_file = path.join(args.output_dir, 'wiki_zh_latest.parquet')
        df.to_parquet(output_file, engine='pyarrow')
    elif args.format == 'txt':
        with open(path.join(args.output_dir, 'wiki_zh_latest.txt'), 'w', encoding='utf-8') as f:
            for text in dataset:
                f.write(text['text'] + '\n')
    else:
        raise ValueError('Invalid format')

    print('Finished!')
    print(f'total: {len(dataset)}, error: {error}')


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--data_folder', type=str)
    args.add_argument('--output_dir', type=str, default='./')
    args.add_argument('--format', type=str, choices=['json', 'jsonl', 'parquet', 'txt'], default='json', help='output format')
    args.add_argument('--remove_input', action='store_true', help='remove input files')
    args = args.parse_args()

    wiki_processing()

    # 使用方式：
    # pip install opencc-python
    # python wiki_parser.py --data_folder /mnt/data/djx/wiki_zh_latest --output_dir ./ --format json --remove_input
