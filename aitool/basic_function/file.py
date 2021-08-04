# -*- coding: UTF-8 -*-
# @Time    : 2020/10/29
# @Author  : xiangyuejia@qq.com
import os
import json
import pickle
import pandas as pd
import inspect
import functools
from typing import Any, List, Union, NoReturn
from aitool import split_dict


def file_exist(file: str) -> bool:
    return os.path.exists(file)


def make_dir(file: str) -> NoReturn:
    path, _ = os.path.split(file)
    if path and not os.path.exists(path):
        os.makedirs(path)


def dump_json(
        obj: Any,
        file: str,
        formatting: bool = False,
        ensure_ascii: bool = False,
        **kwargs,
) -> NoReturn:
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


def dump_pickle(obj: Any, file: str, **kwargs) -> NoReturn:
    make_dir(file)
    with open(file, 'wb') as fw:
        pickle.dump(obj, fw, **kwargs)


def load_pickle(file: str, **kwargs) -> Any:
    if not os.path.isfile(file):
        print('incorrect file path')
        raise Exception
    with open(file, 'rb') as fr:
        return pickle.load(fr, **kwargs)


def dump_lines(data: List[Any], file: str) -> NoReturn:
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


def dump_panda(
        data: List[Any],
        file: str,
        file_format: str,
        dump_index: bool = False,
        **kwargs,
) -> NoReturn:
    make_dir(file)
    if 'index' in kwargs and isinstance(kwargs['index'], bool):
        raise ValueError('The parameter `index` is for pd.DataFrame. '
                         'If want to set the `index` for panda.to_csv/excel please use `dump_index`')
    selected_kwargs, _ = split_dict(kwargs, inspect.getfullargspec(pd.DataFrame).args)
    df = pd.DataFrame(data, **selected_kwargs)
    selected_kwargs, _ = split_dict(kwargs, inspect.getfullargspec(df.to_csv).args)
    selected_kwargs['index'] = dump_index
    if file_format == 'excel':
        df.to_excel(file, **selected_kwargs)
    if file_format == 'csv':
        df.to_csv(file, **selected_kwargs)


dump_csv = functools.partial(dump_panda, file_format='csv')
dump_excel = functools.partial(dump_panda, file_format='excel')


def load_excel(*args, **kwargs) -> List:
    df = pd.read_excel(*args, **kwargs)
    data = df.values
    return data


def load_csv(*args, **kwargs) -> List:
    df = pd.read_csv(*args, **kwargs)
    data = df.values
    return data


if __name__ == '__main__':
    x = [[1, 'a'], [2, 'b']]
    dump_csv(x, 'test.csv', dump_index=True, header=['xx', 'yy'])
    dump_excel(x, 'test.xlsx', dump_index=True, header=['xx', 'yy'])
    dump_csv()
