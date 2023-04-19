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
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
"""

from typing import Dict, Tuple, Union, List, Iterator, Any, NoReturn
from aitool import singleton, pip_install


@singleton
class NLTK:
    def __init__(self):
        self.cut_until_char_delimiter = set('(（[〔【')
        self.delete_char_discard = set(')〕－-”—.“《）')
        self.nick_name_prefix = set('小大老阿男女')
        self.nick_name_postfix_1 = set('哥姐总')
        self.nick_name_postfix_2 = set('甲乙丙丁戊己庚辛壬癸一二三四五六七八九十')


def is_nick_name(text: str, ) -> bool:
    n = NLTK()
    if len(text) == 2:
        if text[0] in n.nick_name_prefix or text[-1] in n.nick_name_postfix_1:
            return True
        if text[0] in n.nick_name_postfix_2 or text[1] in n.nick_name_postfix_2:
            return True
    if len(text) == 3:
        if text[0] in n.nick_name_postfix_2 and text[1] in n.nick_name_postfix_2:
            return True
    return False


def is_contains_english(text: str) -> bool:
    for c in text:
        _ord = ord(c)
        if 65 <= _ord <= 90 or 97 <= _ord <= 122:
            return True
    return False


def cut_until_char(text: str, delimiter: Union[tuple, str, list] = None) -> str:
    if delimiter is None:
        delimiter = NLTK().cut_until_char_delimiter
    for index, char in enumerate(text):
        if char in delimiter:
            return text[:index]
    return text


def delete_char(text: str, discard: Union[tuple, str, list] = None):
    if discard is None:
        discard = NLTK().delete_char_discard
    new_text = ''
    for char in text:
        if char not in discard:
            new_text += char
    return new_text


def is_contains_figure(text: str) -> bool:
    for char in text:
        if char.isdigit():
            return True
    return False


def is_contains_chinese(strs) -> bool:
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fff':
            return True
    return False


def is_all_chinese(text: str) -> bool:
    for char in text:
        if not is_contains_chinese(char):
            return False
    return True


# 获取单词的词性
def get_wordnet_pos(tag):
    try:
        from nltk.corpus import wordnet
    except ModuleNotFoundError:
        pip_install('nltk')
        from nltk.corpus import wordnet

    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def get_word_prototype(word):
    try:
        from nltk import word_tokenize, pos_tag
        from nltk.corpus import wordnet
        from nltk.stem import WordNetLemmatizer
    except ModuleNotFoundError:
        pip_install('nltk')
        from nltk import word_tokenize, pos_tag
        from nltk.corpus import wordnet
        from nltk.stem import WordNetLemmatizer

    tokens = word_tokenize(word)
    tagged_sent = pos_tag(tokens)  # 获取单词词性

    wnl = WordNetLemmatizer()
    lemmas_sent = []
    for tag in tagged_sent:
        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
        lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos))  # 词形还原

    return lemmas_sent[0]


if __name__ == '__main__':
    print(get_word_prototype('books'))
