# -*- coding: UTF-8 -*-
# @Time    : 2020/10/29
# @Author  : xiangyuejia@qq.com
import os
import json
import pickle
from typing import Any


def save_json(file: str, obj: Any) -> None:
    with open(file, 'w', encoding='utf-8') as fw:
        json.dump(obj, fw)


def load_json(file: str) -> Any:
    if not os.path.isfile(file):
        print('incorrect file path')
        raise Exception
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
