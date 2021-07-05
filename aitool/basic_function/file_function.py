# -*- coding: UTF-8 -*-
# @Time    : 2020/10/29
# @Author  : xiangyuejia@qq.com
import os
import json
import pickle
import pandas as pd
from typing import Any, List


def file_exist(file: str):
    return os.path.exists(file)


def save_json(file: str, obj: Any) -> None:
    path, _ = os.path.split(file)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(file, 'w', encoding='utf-8') as fw:
        json.dump(obj, fw)


def load_json(file: str) -> Any:
    if not os.path.isfile(file):
        print('incorrect file path')
        raise FileExistsError
    with open(file, 'r', encoding='utf-8') as fr:
        return json.load(fr)


def save_pickle(obj: Any, file: str) -> None:
    with open(file, 'wb') as fw:
        pickle.dump(obj, fw)


def load_pickle(file: str) -> Any:
    if not os.path.isfile(file):
        print('incorrect file path')
        raise Exception
    with open(file, 'rb') as fr:
        return pickle.load(fr)


def read_lines(file: str) -> List[Any]:
    with open(file, 'r', encoding='utf8') as fin:
        data = [d.strip() for d in fin.readlines()]
    return data


def write_lines(data: List[Any], file: str) -> None:
    with open(file, 'w', encoding='utf8') as fout:
        for d in data:
            print(d, file=fout)


def save_excel(
        data: List[Any],
        file: str,
        index=False,
        header=False
) -> None:
    df = pd.DataFrame(data)
    df.to_excel(file, index=index, header=header)
