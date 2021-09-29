# -*- coding: UTF-8 -*-
# Copyright©2020 xiangyuejia@qq.com All Rights Reserved
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
from aitool import encrypt_md5
from typing import Dict, Union, List, Any, NoReturn


class Deduplication:
    def __init__(self, use_md5: bool = True):
        self.use_md5 = use_md5
        self.data = set()

    def add(self, item: Any) -> NoReturn:
        if not isinstance(item, str):
            item = '{}'.format(item)
        if self.use_md5:
            self.data.add(encrypt_md5(item))
        else:
            self.data.add(item)

    def clean(self):
        self.data = set()

    def is_duplication(self, item: Any, update=True) -> bool:
        if not isinstance(item, str):
            item = '{}'.format(item)
        if self.use_md5:
            item = encrypt_md5(item)
        if item in self.data:
            return True
        else:
            if update:
                self.data.add(item)
        return False


if __name__ == '__main__':
    deduplication = Deduplication()
    for k in [1,2,3,1,2,{1,2},{1,2},set('12'),set('12'),set('21'),set('21'),{1,4}]:
        print(k, '{}'.format(k), deduplication.is_duplication(k))
