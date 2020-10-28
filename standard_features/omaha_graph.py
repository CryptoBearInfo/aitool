# -*- coding: UTF-8 -*-
# @Time    : 2020/10/27
# @Author  : xiangyuejia@qq.com
import os
from aitool.data_structure.graph.chain_forward_stars import ChainForwardStars


class OmahaGraph:
    def __init__(self, paras={}, read_json=False):
        self.term2cpt = {}
        self.cpt2term = {}
        self.c_term2cpt = {}
        self.cpt2c_term = {}
        self.cpt2tag = {}
        self.cpt2top1_name = {}
        self.cpt2icd = {}
        self.icd2cpt = {}
        self.cpt2infer_icd = {}
        self.dis2bod = {}
        self.father = {}
        self.subclass = {}
        self.bod = set()
        self.terms = set()
        # self.json_file_path = os.path.join(data_dir_path,'graph.json')
        self.json_file_path = os.path.join(data_dir_path, 'graph_20200720.json')
        self.init_data(paras=paras, read_json=read_json)