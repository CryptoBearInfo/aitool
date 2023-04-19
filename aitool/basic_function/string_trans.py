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
from typing import Dict, Tuple, Union, List, Iterator, Any, NoReturn
from aitool import deduplicate

def find_all_position(substr: str, text: str) -> List[Tuple[int, int]]:
    """
    找到substr在context里出现的所有位置
    :param substr: 需要查找的文本片段
    :param text: 文本
    :return: substr在context里出现的所有位置
    >>> find_all_position('12', '12312312')
    [(0, 2), (3, 5), (6, 8)]
    """
    return [(i, i + len(substr)) for i in range(len(text)) if text.startswith(substr, i)]


def get_ngram(text: str, ngram: int = 2):
    """
    获取text的所有ngram片段
    :param text: 文本
    :param ngram: 判断的字长
    :return: text的所有ngram片段
    >>> list(get_ngram('abcd'))
    ['ab', 'bc', 'cd']
    """
    for i in range(len(text)-ngram+1):
        yield text[i: i+ngram]


def get_ngrams(text: Union[str, List], min_gram: int, max_gram: int):
    """
    获取text的多个ngram片段
    :param text:
    :param min_gram:
    :param max_gram:
    :return:
    >>> list(get_ngrams('abcd', 1, 3))
    ['a', 'b', 'c', 'd', 'ab', 'bc', 'cd', 'abc', 'bcd']
    >>> list(get_ngrams(['a', 'bc', 'd', 'ef'], 1, 3))
    [['a'], ['bc'], ['d'], ['ef'], ['a', 'bc'], ['bc', 'd'], ['d', 'ef'], ['a', 'bc', 'd'], ['bc', 'd', 'ef']]
    """
    rst = []
    for ngram in range(min_gram, max_gram+1):
        rst.extend(list(get_ngram(text, ngram)))
    return rst


def token_hit(text: str, tokens: Iterator[str]) -> List[str]:
    """
    获取text中包含的token的列表
    :param text: 待处理的文本
    :param tokens: 字符串的列表
    :return: 命中的字符串的列表
    >>> token_hit('1234567', ['1', '34', '9'])
    ['1', '34']
    """
    hit_token = []
    tokens = deduplicate(tokens)
    for token in tokens:
        if token in text:
            hit_token.append(token)
    return hit_token


def filter_keyword(text, keywords, min_count=1):
    keywords = set(keywords)
    keywords_len = [len(k) for k in keywords]
    min_ngram = min(keywords_len)
    max_ngram = max(keywords_len)
    the_grams = set(get_ngrams(text, min_ngram, max_ngram))
    if len(keywords & the_grams) >= min_count:
        return True
    return False


if __name__ == '__main__':
    import doctest

    doctest.testmod()
