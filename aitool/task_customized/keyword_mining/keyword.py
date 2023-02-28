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


@exe_time(print_time=True)
def get_keyword_graph(
        texts: List[str],
        top=10000,
        pos=('ns', 'n', 'vn', 'v'),
        use_short=False,
        short_weight=1.0,
        new=1.0,
        default_keyword=False,
        deduplication=False,
        deny_word=True,
        fix_deny_fragment=True,
        max_len=10,
        new_char=1,
        min_count=3,
        score_negative=1.0,
        score_positive=-0.1,
) -> Tuple[List, List, Any]:
    """
    输入一组文本。提取关键词和边。
    :param texts: 一组文本
    :param top: 保留原始keyword的个数
    :param pos: 保留原始keyword的词性
    :param use_short: 保留短词
    :param short_weight: 短词的权重，权重越高短词排序越靠前
    :param mix_short: 输出短词
    :param new: 新颖性得分权重
    :param default_keyword: False时从输入的文本中计算关键词，True时用实现计算好的（此时deduplication无效）。
    :param deduplication: 对输入的文本去重
    :param deny_word: 是否向词表中加入所有否定词
    :param fix_deny_fragment: 是否补齐短语前的否定词
    :param max_len: 短语的最大长度
    :param new_char: 短语必须包含至少new_char个新的字
    :param min_count: 短语至少重复出现min_count次
    :param score_negative: 负向情感加分
    :param score_positive: 正向情感加分
    :return: 节点表，边表，附加信息
    """
    tfidf = jieba.analyse.TFIDF()
    stm = Sentiment()

    # 确保texts里都是字符串
    texts = list(map(str, texts))

    # 记录key的相关信息
    keyword2score = {}
    keyword_filtered = set()
    keyword2count = defaultdict(int)
    keyword2sentence = defaultdict(list)
    keyword2sentiment = {}
    keyword2sentiment_negative = {}

    if default_keyword:
        # 使用预先计算好的keyword（从1000万个视频标题文本计算得到）
        keyword2score_all = load_pickle(path.join(DATAPATH, 'keyword.pkl'))
        meet_word = set()
        for sentence in tqdm(texts, 'select default keyword'):
            meet_word |= set(list(tfidf.tokenizer.cut(sentence)))
        for k, v in keyword2score_all.items():
            if k in meet_word:
                keyword2score[k] = v
    else:
        # 不使用预先计算好的keyword
        if deduplication:
            texts = list(set(texts))
        concat_text = '\n'.join(texts)
        print('sentence:', len(texts), 'char', len(concat_text))
        keyword2score = get_keyword(concat_text, top=top, pos=pos)
    keyword_set = set(list(keyword2score.keys()))

    # 作为单独输出的短词，要求全中文
    for kw in keyword_set:
        if not is_all_chinese(kw):
            continue
        keyword_filtered.add(kw)
        sentiment_score = stm.score(kw)
        keyword2sentiment[kw] = abs(sentiment_score)
        keyword2sentiment_negative[kw] = 0
        if sentiment_score == -1:
            keyword2sentiment_negative[kw] = 1

    # 导入否定词,并给定一个固定的分数
    deny_word_set = set(load_lines(path.join(DATAPATH, 'deny.txt')))
    if deny_word:
        for word in deny_word_set:
            if word not in keyword2score:
                keyword2score[word] = 0.1
        keyword_set = keyword_set | deny_word_set
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
    for sentence in tqdm(texts, 'connect keypair'):
        sp = list(tfidf.tokenizer.cut(sentence))
        # 记录关键词的信息
        kw_record = set()  # 避免重复记录到keyword2sentence
        for kw in sp:
            if kw in keyword_filtered:
                keyword2count[kw] += 1
                if kw not in kw_record:
                    kw_record.add(kw)
                    if len(keyword2sentence[kw]) < 10:
                        keyword2sentence[kw].append(sentence)

        # 计算关键词的下标位置
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
            if fix_deny_fragment:
                if sentence[max(sp_pos_select[i][1]-3, 0):sp_pos_select[i][1]] in deny_word_set:
                    fragment = sentence[max(sp_pos_select[i][1]-3, 0):sp_pos_select[i][1]] + fragment
                elif sentence[max(sp_pos_select[i][1]-2, 0):sp_pos_select[i][1]] in deny_word_set:
                    fragment = sentence[max(sp_pos_select[i][1]-2, 0):sp_pos_select[i][1]] + fragment
                elif sentence[max(sp_pos_select[i][1]-1, 0):sp_pos_select[i][1]] in deny_word_set:
                    fragment = sentence[max(sp_pos_select[i][1]-1, 0):sp_pos_select[i][1]] + fragment
            # 仅保留全中文的短语
            if not is_all_chinese(fragment):
                continue
            # 去除过长的短语
            if len(fragment) > max_len:
                continue
            kp = sp_pos_select[i][0] + sp_pos_select[i + 1][0]
            kp_distance = -sp_pos_select[i][1] - len(sp_pos_select[i][0]) + sp_pos_select[i + 1][1]
            keypair2distance[kp].append(kp_distance)
            keypair2id[kp] = (keyword2id[sp_pos_select[i][0]], keyword2id[sp_pos_select[i + 1][0]])
            keypair2fragment[kp].append(fragment)
            if len(keypair2sentence[kp]) < 10:
                keypair2sentence[kp].append(sentence)
            keypair_score_sum[kp] = keyword2score[sp_pos_select[i][0]] + keyword2score[sp_pos_select[i + 1][0]]
    print('find keypair', len(keypair_score_sum))
    # keypair算特征
    keypair2times = {}
    keypair2distance_average = {}
    keypair2best_fragment = {}
    keypair2sentiment = {}
    keypair2sentiment_negative = {}

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
    # all_feature 里仅在最后加新特征，不要改动前面特征的顺序
    # TODO 这种数据结构不好
    all_feature = []
    keypair2rank_score = {}
    for kp in keypair2id.keys():
        keypair2rank_score[kp] = 0
        keypair2rank_score[kp] += keypair_score_sum[kp]
        if keypair2times[kp] > 100:
            keypair2rank_score[kp] += 0.8
        elif keypair2times[kp] > 10:
            keypair2rank_score[kp] += 0.3
        keypair2rank_score[kp] += keypair2sentiment_negative[kp] * score_negative
        keypair2rank_score[kp] += (keypair2sentiment[kp]-keypair2sentiment_negative[kp]) * score_positive
        all_feature.append([kp, keypair2sentence[kp], keypair_score_sum[kp], keypair2times[kp],
                            keypair2distance_average[kp], keypair2best_fragment[kp], keypair2sentiment[kp],
                            keypair2sentiment_negative[kp], keypair2rank_score[kp]])

    # 加入短词
    if use_short:
        keyword2rank_score = {}
        for kw in keyword_filtered:
            keyword2rank_score[kw] = keyword2score[kw] \
                                     + 0.8 if keyword2count[kw] > 100 else 0.3 if keyword2count[kw] > 10 else 0 \
                                     + keyword2sentiment_negative[kw] * score_negative\
                                     + (keyword2sentiment[kw]-keyword2sentiment_negative[kw]) * score_positive
            keyword2rank_score[kw] = keyword2rank_score[kw] * short_weight
            all_feature.append([kw, keyword2sentence[kw], keyword2score[kw], keyword2count[kw],
                               0, kw, keyword2sentiment[kw],
                               keyword2sentiment_negative[kw], keyword2rank_score[kw]])

    # 筛选短语
    all_feature.sort(key=lambda _: _[8], reverse=True)
    kp2feature_idx = {}
    for idx, kpl in enumerate(all_feature):
        kp2feature_idx[kp] = idx

    keypair_selected = []
    keypair_selected2rank_score = {}
    char_selected = set()

    for idx, kpl in enumerate(all_feature):
        kp = kpl[0]
        kp2feature_idx[kp] = idx
        # 去除有显著重复的短语
        _char = set(kpl[5])
        if len(_char - char_selected) <= new_char:
            continue
        # 去除出现次数过少的短语
        if kpl[3] < min_count:
            continue
        keypair_selected.append(kp)
        keypair_selected2rank_score[kp] = kpl[8]
        char_selected |= _char
    print('select keypair', len(keypair_selected))

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
        kp_feature = all_feature[kp2feature_idx[kp]]
        node.append([
            kp_feature[5],
            kp_feature[8],
            kp_feature[1],
            kp_feature[3],
            kp_feature[2],
        ])

    # 构建边
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

    def get_sentence_keyword(self, sentence, use_label=False):
        # 取标签
        label = []
        label_text = sentence.split('#', 1)
        if len(label_text) >= 2:
            label_ori = label_text[1].split('#')
            for _l in label_ori:
                strip_l = _l.strip()
                if len(strip_l) > 0:
                    label.append(strip_l)
        # 提取fragment
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
        if use_label:
            rst.extend([_ for _ in label if len(_) > 3])
            rst = list(set(rst))
        if rst:
            return rst
        # 挖掘结果为空时兜底策略
        if label:
            return label
        # 取短词
        # if word_select:
        #     return list(word_select)
        # 原句的最后一个片段。如果是'。。。'则返回[]
        pieces = split_punctuation(sentence)
        if len(pieces) >= 1:
            return [split_punctuation(sentence)[-1]]
        else:
            return []


def get_keyword_graph4panda(info, **kwargs):
    # info 的格式为comment_id	group_id	text
    # todo 计算vv的逻辑可以优化
    info_list = np2list(info)
    texts = []
    text2info = {}
    for comment_id, group_id, vv, text in info_list:
        if text != text:
            continue
        if text == '':
            continue
        texts.append(text)
        if vv == 'NULL':
            vv = 0
        elif vv != vv:  # NaN
            vv = 0
        else:
            vv = int(vv)
        text2info[text] = (comment_id, group_id, vv)
    rst, node, rel = get_keyword_graph(texts, **kwargs)
    node_detail = []
    for kp, rank_score, sents, times, score_sum in node:
        svv = 0
        detail = []
        for _text in text2info.keys():
            if kp in _text:
                svv += text2info[_text][2]
        for sent in sents:
            if sent in text2info:
                detail.append({'text': sent, 'comment_id':text2info[sent][0], 'group_id':text2info[sent][1]})
        node_detail.append([kp, rank_score, svv, detail])
    return node_detail, rel


if __name__ == '__main__':
    data = [
        '纨绔的游戏，不知道正义能不能到来',
        '严打之下，应该没有保护伞。恶魔，早点得到应有的报应。',
        '父母什么责任？？你24小时跟着你14岁的孩子的吗？',
        '我要当父亲别说三个了，他三家人都要去团聚[抠鼻][抠鼻]',
        '不是有意违规',
        '怎么就违规了'
    ]
    _, n, r = get_keyword_graph(
        data,
        use_short=True,
        deny_word=False,
        max_len=6,
        top=5000,
        score_negative=0,
        deduplication=False,
        min_count=1,
        pos=(),
    )
    for _ in n:
        print(_)

    # xx = SentenceKeyword()
    # for s in data:
    #     print(s)
    #     print(xx.get_sentence_keyword(s))

    # all_feature, node, relation = get_keyword_graph(data)
    # print(node)
    # print(relation)

    # SentenceKeyword.update_keyword('./mini.csv')

    # data = load_excel('./mini.xlsx')

    # print(get_keyword_graph4panda(data, default_keyword=True))

    # text = '我只是发表了一下我状态嘛，因为我是修脚师吗？'
    # sk = SentenceKeyword()
    # print(sk.get_sentence_keyword(text, use_label=True))
