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


def print_color(text, color='red'):
    if color == 'red':
        print("\033[31m{}\033[0m".format(text))
    elif color == 'green':
        print("\033[32m{}\033[0m".format(text))
    elif color == 'yellow':
        print("\033[33m{}\033[0m".format(text))
    elif color == 'blue':
        print("\033[34m{}\033[0m".format(text))
    else:
        raise ValueError(color)


def print_red(text):
    print_color(text, color='red')


def print_green(text):
    print_color(text, color='green')


def print_yellow(text):
    print_color(text, color='yellow')


def print_blue(text):
    print_color(text, color='blue')


if __name__ == '__main__':
    print_red('A')
    print_green('A')
    print_yellow('A')
    print_blue('A')
