# in-package data path
from aitool.datasets import PATH as DATAPATH
# web data path
from aitool.datasets import WEB as WEBPATH

# BASIC FUNCTION
from aitool.basic_function.display import print_color, print_red, print_green, print_yellow, print_blue
from aitool.basic_function.singleton import singleton
from aitool.basic_function.pip_tool import pip_install_by_os, pip_install_by_main, pip_install

from aitool.basic_function.basic import split_dict, replace_char, split_char, split_punctuation, is_appear
from aitool.basic_function.deduplication import Deduplication, deduplicate
from aitool.basic_function.string_trans import find_all_position, get_ngram, get_ngrams, token_hit, filter_keyword
from aitool.basic_function.distribution import normalize, cross_entropy, scale_array
from aitool.basic_function.security import encrypt_md5
from aitool.basic_function.path import get_user_root_path
from aitool.basic_function.random_str import random_base64
from aitool.basic_function.file import is_writable, file_exist, is_file_exist, is_file, is_folder, make_dir, \
    is_file_hidden, get_file, add_python_path
from aitool.basic_function.file import dump_json, load_json, dump_pickle, load_pickle, dump_lines, load_big_data, \
    load_byte, load_line, load_lines, dump_excel, load_excel, dump_csv, load_csv
from aitool.basic_function.file import zip, unzip, split_path
from aitool.basic_function.download.download import download_file, get_download_dir, get_aitool_data_path, prepare_data
from aitool.basic_function.format_data import flatten, html2text, content2text, split_part, get_pair, np2list, \
    get_most_item, dict2ranked_list
from aitool.basic_function.word import is_contains_english, cut_until_char, delete_char, is_contains_figure, \
    is_contains_chinese, is_all_chinese, is_nick_name
from aitool.basic_function.exe_time import exe_time
from aitool.basic_function.retry import retry
from aitool.basic_function.time import timeout, timestamp, get_lastday_timestamp

# cache 管理工具
from aitool.basic_function.cache import cache, get_cache, Cache

# 多进程
from aitool.basic_function.multi import pool_map, pool_starmap, multi_map, get_functions, multi

# ARITHMETIC FUNCTION
from aitool.data_structure.arithmetic.dfs_search import Node, dfs, ranked_permutation

# NLP FUNCTION
from aitool.nlp.basic.split_sentence import split_sentence
from aitool.nlp.basic.conditional_probability import conditional_probability
from aitool.nlp.basic.phoneticize import get_pinyin
from aitool.nlp.basic.ngram_tf_idf import get_ngram_tf, get_ngram_idf
from aitool.nlp.sentiment_analysis.dict_match import Sentiment
from aitool.nlp.sentiment_analysis.text_similar import load_word2vec, cos_sim, VectorSim, vector_sim, char_sim, de_sim, \
    generate_offline_sim
from aitool.nlp.chatgpt.chatgpt import chatgpt

# knowledge_graph
from aitool.knowledge_graph.paris.examples.core_example import alignment

# task_customized
from aitool.task_customized.ip_enhance.filter import has_family_name, is_common_word, is_stop_word, \
    is_relationship_title, delete_age_describe, is_black_name, clean_role, clean_alias, delete_nested_text, \
    select_nested_text, is_sub_ip, get_core_ip
