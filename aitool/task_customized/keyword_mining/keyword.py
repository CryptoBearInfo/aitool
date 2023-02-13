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
from os import path
from tqdm import tqdm
from collections import defaultdict, Counter
import jieba.analyse
from typing import Dict, Union, List, Any, NoReturn, Tuple
from aitool import DATAPATH, is_all_chinese, get_most_item
from aitool.nlp.sentiment_analysis.dict_match import Sentiment
from random import random


def get_keyword(text, method='idf') -> dict:
    """
    获取关键词和权重
    :param text:
    :param method:
    :return:
    """
    keyword2score = {}
    jieba.analyse.set_stop_words(path.join(DATAPATH, 'stopwords.txt'))
    if method == 'idf':
        extract = jieba.analyse.extract_tags(text, topK=10000, withWeight=True, allowPOS=('ns', 'n', 'vn', 'v'))
    elif method == 'textrank':
        extract = jieba.analyse.textrank(text, topK=10000, withWeight=True, allowPOS=('ns', 'n', 'vn', 'v'))
    else:
        extract = []
    for key, score in extract:
        keyword2score[key] = score
    return keyword2score


def get_keyword_graph(texts: List[str]) -> Tuple[List, List, Any]:
    """
    输入一组文本。提取关键词和边。
    :param texts: 一组文本
    :return: 节点表，边表，附加信息
    """
    concat_text = '\n'.join(texts)
    print('sentence:', len(texts), 'char', len(concat_text))
    keyword2score = get_keyword(concat_text)
    # 构建keyword2id，和用于记录keyword间共现关系的二维数组keyword_relation
    keyword_list = list(keyword2score.keys())
    keyword_set = set(keyword_list)
    keyword_len = len(keyword_set)
    keyword2id = {}
    id2keyword = {}
    for _id, _k in enumerate(keyword_list):
        keyword2id[_k] = _id
        id2keyword[_id] = _k
    keyword_relation = [[0] * keyword_len for _ in range(keyword_len)]
    # 记录keypair的相关信息
    keypair2distance = defaultdict(list)   # 两个关键词间的距离
    keypair2id = {}
    keypair2fragment = defaultdict(list)
    keypair2sentence = defaultdict(list)
    keypair_score_sum = defaultdict(int)
    tfidf = jieba.analyse.TFIDF()
    for sentence in tqdm(texts, 'connect keypair'):
        sp = list(tfidf.tokenizer.cut(sentence))
        sp_pos = [[sp[i], len(''.join(sp[:i]))] for i in range(len(sp))]
        sp_word = set(sp)
        word_select = sp_word & keyword_set
        sp_pos_select = [[_k, _p] for _k, _p in sp_pos if _k in word_select]
        # 统计单各词直接的有向共现
        for i in range(len(sp_pos_select) - 1):
            for j in range(i + 1, len(sp_pos_select)):
                wi = keyword2id[sp_pos_select[i][0]]
                wj = keyword2id[sp_pos_select[j][0]]
                keyword_relation[wi][wj] += 1
        # 构建组合词, 组合两个不同的关键词
        for i in range(len(sp_pos_select) - 1):
            if sp_pos_select[i][0] == sp_pos_select[i + 1][0]:
                continue
            fragment = sentence[sp_pos_select[i][1]:sp_pos_select[i + 1][1] + len(sp_pos_select[i + 1][0])]
            if not is_all_chinese(fragment):
                continue
            kp = sp_pos_select[i][0] + sp_pos_select[i + 1][0]
            kp_distance = -sp_pos_select[i][1] - len(sp_pos_select[i][0]) + sp_pos_select[i + 1][1]
            keypair2distance[kp].append(kp_distance)
            keypair2id[kp] = (keyword2id[sp_pos_select[i][0]], keyword2id[sp_pos_select[i + 1][0]])
            keypair2fragment[kp].append(fragment)
            if len(keypair2sentence[kp]) < 5:
                keypair2sentence[kp].append(sentence)
            keypair_score_sum[kp] = keyword2score[sp_pos_select[i][0]] + keyword2score[sp_pos_select[i + 1][0]]
    # keypair算特征
    keypair2times = {}
    keypair2distance_average = {}
    keypair2best_fragment = {}
    keypair2sentiment = {}
    keypair2sentiment_negative = {}
    stm = Sentiment()
    for kp, (id1, id2) in tqdm(keypair2id.items(), 'analysis keypair'):
        # 出现次数
        keypair2times[kp] = len(keypair2distance[kp])
        # 平均距离
        keypair2distance_average[kp] = sum(keypair2distance[kp])/keypair2times[kp]
        # 最频繁段短语
        keypair2best_fragment[kp] = get_most_item(keypair2fragment[kp], all_chinese=True)
        # 情感倾向
        keypair2sentiment_negative[kp] = 0
        if stm.score(id2keyword[keypair2id[kp][0]]) == -1:
            keypair2sentiment_negative[kp] += 1
        if stm.score(id2keyword[keypair2id[kp][1]]) == -1:
            keypair2sentiment_negative[kp] += 1
        keypair2sentiment[kp] = abs(stm.score(id2keyword[keypair2id[kp][0]])) + \
                                abs(stm.score(id2keyword[keypair2id[kp][1]]))
    # 对特征汇总并计算排序分
    all_feature = []
    keypair2rank_score = {}
    for kp in keypair2id.keys():
        keypair2rank_score[kp] = 0
        keypair2rank_score[kp] += keypair_score_sum[kp]
        if keypair2times[kp] > 100:
            keypair2rank_score[kp] += 0.8
        elif keypair2times[kp] > 10:
            keypair2rank_score[kp] += 0.3
        keypair2rank_score[kp] += keypair2sentiment_negative[kp]
        keypair2rank_score[kp] += (keypair2sentiment_negative[kp]-keypair2sentiment[kp]) * 0.1
        all_feature.append([kp, keypair2sentence[kp], keypair_score_sum[kp], keypair2times[kp],
                            keypair2distance_average[kp], keypair2best_fragment[kp], keypair2sentiment[kp],
                            keypair2sentiment_negative[kp], keypair2rank_score[kp]])
    # 筛选出没有显著重复的词
    all_feature.sort(key=lambda _: _[-1], reverse=True)
    keypair_selected = []
    char_selected = set()
    for kpl in all_feature:
        kp = kpl[0]
        _char = set(keypair2best_fragment[kp])
        if len(_char - char_selected) >= 2:
            keypair_selected.append(kp)
            char_selected |= _char
    # 整理出node表
    node = []
    for kp in keypair_selected:
        node.append([keypair2best_fragment[kp], keypair2rank_score[kp], keypair2sentence[kp]])
    # 构建虚假的边集和
    relation = []
    len_node = len(node)
    for i in range(len_node):
        for j in range(i+1, len_node):
            if random() < 1/(j-i+1):
                relation.append([node[i][0], node[j][0], node[i][1]+node[j][1]])
    return all_feature, node, relation


if __name__ == '__main__':
    data = [
        '纨绔的游戏，不知道正义能不能到来',
        '严打之下，应该没有保护伞。恶魔，早点得到应有的报应。',
        '父母什么责任？？你24小时跟着你14岁的孩子的吗？',
        '我要当父亲别说三个了，他三家人都要去团聚[抠鼻][抠鼻]',
    ]
    rst = get_keyword_graph(data)
    print(rst)
