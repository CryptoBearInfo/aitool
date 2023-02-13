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
from aitool import load_lines, DATAPATH
from os import path


class Sentiment:
    def __init__(self):
        negative_path = path.join(DATAPATH, 'negative.txt')
        positive_path = path.join(DATAPATH, 'positive.txt')
        self.negative = set(load_lines(negative_path))
        self.positive = set(load_lines(positive_path))

    def score(self, word):
        if word in self.negative:
            return -1
        if word in self.positive:
            return 1
        return 0
