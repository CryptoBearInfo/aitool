# -*- coding: UTF-8 -*-
# @Time    : 2020/10/29
# @Author  : xiangyuejia@qq.com
import os
import json
import pickle
import pandas as pd
from typing import Any, List, Union


def file_exist(file: str):
    return os.path.exists(file)


def make_dir(file: str):
    path, _ = os.path.split(file)
    if path and not os.path.exists(path):
        os.makedirs(path)


def dump_json(
        obj: Any,
        file: str,
        formatting: bool = False,
        ensure_ascii: bool = False,
        **kwargs,
) -> None:
    make_dir(file)
    kwargs['ensure_ascii'] = ensure_ascii
    if formatting:
        kwargs['sort_keys'] = True
        kwargs['indent'] = 4
        kwargs['separators'] = (',', ':')
    with open(file, 'w', encoding='utf-8') as fw:
        json.dump(obj, fw, **kwargs)


def load_json(file: str, **kwargs,) -> Any:
    if not os.path.isfile(file):
        print('incorrect file path')
        raise FileExistsError
    with open(file, 'r', encoding='utf-8') as fr:
        return json.load(fr, **kwargs,)


def dump_pickle(obj: Any, file: str, **kwargs) -> None:
    make_dir(file)
    with open(file, 'wb') as fw:
        pickle.dump(obj, fw, **kwargs)


def load_pickle(file: str, **kwargs) -> Any:
    if not os.path.isfile(file):
        print('incorrect file path')
        raise Exception
    with open(file, 'rb') as fr:
        return pickle.load(fr, **kwargs)


def dump_lines(data: List[Any], file: str) -> None:
    make_dir(file)
    with open(file, 'w', encoding='utf8') as fout:
        for d in data:
            print(d, file=fout)


def load_lines(file: str, separator: Union[None, str] = None) -> List[Any]:
    data = []
    with open(file, 'r', encoding='utf8') as fin:
        for d in fin.readlines():
            item = d.strip()
            if separator:
                item = item.split(separator)
            data.append(item)
    return data


def dump_excel(
        data: List[Any],
        file: str,
        **kwargs,
) -> None:
    make_dir(file)
    df = pd.DataFrame(data)
    df.to_excel(file, **kwargs)


def load_excel(*args, **kwargs) -> List:
    df = pd.read_excel(*args, **kwargs)
    data = df.values
    return data


if __name__ == '__main__':
    x = [1,2,[2,4],{1:2,5:'222'}]
    dump_json(x, 'test.json', formatting=True)
