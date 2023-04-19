# -*- coding: UTF-8 -*-
# Copyright©2022 xiangyuejia@qq.com All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

"""
from typing import Dict, Union, List, Any, NoReturn, Tuple
import numpy as np


def normalize(v: List[int]):
    # 单位向量化
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return (v / norm).tolist()


def cross_entropy(a: List[float], b: List[float]):
    assert len(a) == len(b)
    a = np.array(a)
    b = np.array(b)
    # 添加一个微小值可以防止负无限大(np.log(0))的发生。
    delta = 1e-7
    return -np.sum(b * np.log(a + delta))


def scale_array(dat: List[float], out_range=(-1, 1)):
    dat = np.array(dat)

    # 使数组变化到目标范围内
    domain = [np.min(dat, axis=0), np.max(dat, axis=0)]

    def _interp(_x):
        return out_range[0] * (1.0 - _x) + out_range[1] * _x

    def _uninterp(_x):
        if (domain[1] - domain[0]) != 0:
            b = domain[1] - domain[0]
        else:
            b = 1.0 / domain[1]
        return (_x - domain[0]) / b

    return _interp(_uninterp(dat)).tolist()


if __name__ == '__main__':
    x = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    y = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    print(cross_entropy(y, x))
    y = [0, 0, 0.8, 0, 0, 0.2, 0, 0, 0, 0]
    print(cross_entropy(y, x))
    y = [0, 0, 0.5, 0, 0, 0.5, 0, 0, 0, 0]
    print(cross_entropy(y, x))
    y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    print(cross_entropy(y, x))
    y = [0.1, 0.05, 0.6, 0.0, 0.05, 0.1, 0.0, 0.1, 0.0, 0.0]
    print(cross_entropy(y, x))
    y = [0.1, 0.05, 0.1, 0.0, 0.05, 0.1, 0.0, 0.6, 0.0, 0.0]
    print(cross_entropy(y, x))
    y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    print(cross_entropy(y, x))

    print(normalize([1, 2, 3, 4, 0]))

    print(scale_array([-2, 0, 2]))
    print(scale_array([-3, -2, -1]))
    print(scale_array([1, 2, 3, 4]))
    print(scale_array([1, 2, 3, 4], out_range=(10, 100)))
    print(scale_array([-4, -2, -2, 3, 10], out_range=(10, 100)))
    print(scale_array([-4, -2, -2, 3, 10], out_range=(100, 10)))
