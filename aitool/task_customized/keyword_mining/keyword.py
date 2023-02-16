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
from aitool import DATAPATH, is_all_chinese, get_most_item, load_lines, dump_pickle, load_pickle, exe_time, load_excel, np2list
from aitool.basic_function.basic import split_punctuation
from aitool.nlp.sentiment_analysis.dict_match import Sentiment
from random import random


def get_keyword(text, method='idf', top=10000, pos=('ns', 'n', 'vn', 'v')) -> dict:
    """
    获取关键词和权重
    :param text:
    :param method:
    :param top:
    :param pos:
    :return:
    """
    keyword2score = {}
    jieba.analyse.set_stop_words(path.join(DATAPATH, 'stopwords.txt'))
    if method == 'idf':
        extract = jieba.analyse.extract_tags(text, topK=top, withWeight=True, allowPOS=pos)
    elif method == 'textrank':
        extract = jieba.analyse.textrank(text, topK=top, withWeight=True, allowPOS=pos)
    else:
        extract = []
    for key, score in extract:
        keyword2score[key] = score
    return keyword2score


def get_fragment():
    # 候选考虑将此模块独立
    # 支持不同的拼接方案：相邻的词、隔1个的词
    pass


def get_keyword_graph(
        texts: List[str],
        top=10000,
        pos=('ns', 'n', 'vn', 'v'),
        new=1.0,
        default_keyword=False,
) -> Tuple[List, List, Any]:
    """
    输入一组文本。提取关键词和边。
    :param texts: 一组文本
    :param top:
    :param pos:
    :param new: 新颖性得分权重
    :param default_keyword:
    :return: 节点表，边表，附加信息
    """
    if default_keyword:
        # 使用预先计算好的keyword（从1000万个视频标题文本计算得到）
        keyword2score = load_pickle(path.join(DATAPATH, 'keyword.pkl'))
    else:
        # 不使用预先计算好的keyword
        concat_text = '\n'.join(texts)
        print('sentence:', len(texts), 'char', len(concat_text))
        keyword2score = get_keyword(concat_text, top=top, pos=pos)
    # 导入否定词,并给定一个固定的分数
    deny_word_set = set(load_lines(path.join(DATAPATH, 'deny.txt')))
    for word in deny_word_set:
        if word not in keyword2score:
            keyword2score[word] = 0.1
    # 额外添加否定词
    keyword_set = set(list(keyword2score.keys())) | deny_word_set
    keyword_len = len(keyword_set)
    keyword2id = {}
    id2keyword = {}
    for _id, _k in enumerate(keyword_set):
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
            # 检查fragment前的否定词,仅考虑最多3个词
            if sentence[max(sp_pos_select[i][1]-3, 0):sp_pos_select[i][1]] in deny_word_set:
                fragment = sentence[max(sp_pos_select[i][1]-3, 0):sp_pos_select[i][1]] + fragment
            elif sentence[max(sp_pos_select[i][1]-2, 0):sp_pos_select[i][1]] in deny_word_set:
                fragment = sentence[max(sp_pos_select[i][1]-2, 0):sp_pos_select[i][1]] + fragment
            elif sentence[max(sp_pos_select[i][1]-1, 0):sp_pos_select[i][1]] in deny_word_set:
                fragment = sentence[max(sp_pos_select[i][1]-1, 0):sp_pos_select[i][1]] + fragment
            # 仅保留全中文的短语
            if not is_all_chinese(fragment):
                continue
            kp = sp_pos_select[i][0] + sp_pos_select[i + 1][0]
            kp_distance = -sp_pos_select[i][1] - len(sp_pos_select[i][0]) + sp_pos_select[i + 1][1]
            keypair2distance[kp].append(kp_distance)
            keypair2id[kp] = (keyword2id[sp_pos_select[i][0]], keyword2id[sp_pos_select[i + 1][0]])
            keypair2fragment[kp].append(fragment)
            if len(keypair2sentence[kp]) < 10:
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
    keypair_selected2rank_score = {}
    char_selected = set()
    for kpl in all_feature:
        kp = kpl[0]
        _char = set(keypair2best_fragment[kp])
        if len(_char - char_selected) >= 2:
            keypair_selected.append(kp)
            keypair_selected2rank_score[kp] = keypair2rank_score[kp]
            char_selected |= _char
    # 对入选的词做新颖性加分
    keypair_selected_new = []
    word_count = defaultdict(int)
    word_whole = 0
    for kp, score in keypair_selected2rank_score.items():
        word_count_avg = (word_whole+1)/(len(word_count)+1)
        new_score = 0
        for _char in kp:
            if word_count[_char] < word_count_avg:
                new_score += 1 - word_count[_char] / word_count_avg
            word_count[_char] += 1
            word_whole += 1
        new_score /= len(kp)
        new_score *= new
        keypair_selected_new.append([kp, keypair_selected2rank_score[kp] + new_score])
    keypair_selected_new.sort(key=lambda _: _[1], reverse=True)
    # 整理出node表
    node = []
    for kp, score in keypair_selected_new:
        node.append([keypair2best_fragment[kp], keypair2rank_score[kp], keypair2sentence[kp]])
    # 构建虚假的边集和
    relation = []
    len_node = len(node)
    for i in range(len_node):
        for j in range(i+1, len_node):
            if random() < 1/(j-i+1+i/30):
                relation.append([node[i][0], node[j][0], node[i][1]+node[j][1]])
    return all_feature, node, relation


class SentenceKeyword:
    def __init__(self):
        keyword2score = load_pickle(path.join(DATAPATH, 'keyword.pkl'))
        keyword_list = list(keyword2score.keys())
        print('len keyword', len(keyword_list))
        self.keyword_set = set(keyword_list)
        self.tfidf = jieba.analyse.TFIDF()

    @classmethod
    @exe_time(print_time=True)
    def update_keyword(cls, doc_file, top=1000000):
        texts = load_lines(doc_file)
        print(len(texts))
        texts = texts[:10000000]
        print('#################')
        concat_text = '\n'.join(texts)
        keyword2score = get_keyword(concat_text, top=top)
        dump_pickle(keyword2score, path.join(DATAPATH, 'keyword.pkl'))

    def get_sentence_keyword(self, sentence):
        sp = list(self.tfidf.tokenizer.cut(sentence))
        sp_pos = [[sp[i], len(''.join(sp[:i]))] for i in range(len(sp))]
        sp_word = set(sp)
        word_select = sp_word & self.keyword_set
        sp_pos_select = [[_k, _p] for _k, _p in sp_pos if _k in word_select]
        rst = []
        for i in range(len(sp_pos_select) - 1):
            if sp_pos_select[i][0] == sp_pos_select[i + 1][0]:
                continue
            fragment = sentence[sp_pos_select[i][1]:sp_pos_select[i + 1][1] + len(sp_pos_select[i + 1][0])]
            if not is_all_chinese(fragment):
                continue
            if len(fragment) >= 10:
                continue
            rst.append(fragment)
        if rst:
            return rst
        # 挖掘结果为空时兜底策略
        # 取标签
        label = []
        label_text = sentence.split('#', 1)
        if len(label_text) >= 2:
            label = label_text[1].split('#')
        if label:
            return label
        # 取短词
        # if word_select:
        #     return list(word_select)
        # 原句
        return [split_punctuation(sentence)[-1]]


def get_keyword_graph4panda(info, **kwargs):
    # info 的格式为comment_id	group_id	text
    info_list = np2list(info)
    texts = []
    text2info = {}
    for comment_id, group_id, text in info_list:
        texts.append(text)
        text2info[text] = (comment_id, group_id)
    rst, node, rel = get_keyword_graph(texts, **kwargs)
    node_detail = []
    for kp, score, sents in node:
        detail = []
        for sent in sents:
            if sent in text2info:
                detail.append({'text': sent, 'comment_id':text2info[sent][0], 'group_id':text2info[sent][1]})
        node_detail.append([kp, score, detail])
    return node_detail, rel


if __name__ == '__main__':
    # data = [
    #     '纨绔的游戏，不知道正义能不能到来',
    #     '严打之下，应该没有保护伞。恶魔，早点得到应有的报应。',
    #     '父母什么责任？？你24小时跟着你14岁的孩子的吗？',
    #     '我要当父亲别说三个了，他三家人都要去团聚[抠鼻][抠鼻]',
    #     '不是有意违规',
    #     '怎么就违规了'
    # ]
    # xx = SentenceKeyword()
    # for s in data:
    #     print(s)
    #     print(xx.get_sentence_keyword(s))

    # all_feature, node, relation = get_keyword_graph(data)
    # print(node)
    # print(all_feature, node, relation)

    # SentenceKeyword.update_keyword('/Users/bytedance/Downloads/281474998307169-point_extend-拉取大量标题-查询4.csv')

    data = load_excel('/Users/bytedance/PycharmProjects/textgraph/南宁杀人_mini.xlsx')
    # print(get_keyword_graph4panda(data))
    print(get_keyword_graph4panda(data, default_keyword=True))
