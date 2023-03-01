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
from typing import Dict, Tuple, Union, List, Iterator, Any, NoReturn, Callable
import sys
from urllib import request, error
from aitool import WEBPATH, make_dir, is_file_exist, is_writable, unzip
import requests
import os
import warnings
import math
from enum import Enum
from tqdm import tqdm
# TODO 最基础的网络下载能力，后续download/utils里的修改为复用本文件里的方法


def get_download_dir():
    """
    Return the directory to which packages will be downloaded by default.
    """
    # common path
    paths = []
    if sys.platform.startswith("win"):
        paths += [
            os.path.join(sys.prefix, "aitool_data"),
            os.path.join(sys.prefix, "share", "aitool_data"),
            os.path.join(sys.prefix, "lib", "aitool_data"),
            os.path.join(os.environ.get("APPDATA", "C:\\"), "aitool_data"),
            r"C:\aitool_data",
            r"D:\aitool_data",
            r"E:\aitool_data",
        ]
    else:
        paths += [
            os.path.join(sys.prefix, "aitool_data"),
            os.path.join(sys.prefix, "share", "aitool_data"),
            os.path.join(sys.prefix, "lib", "aitool_data"),
            "/usr/share/aitool_data",
            "/usr/local/share/aitool_data",
            "/usr/lib/aitool_data",
            "/usr/local/lib/aitool_data",
        ]
    for path in paths:
        if is_file_exist(path) and is_writable(path):
            return path

    # On Windows, use %APPDATA%
    if sys.platform == "win32" and "APPDATA" in os.environ:
        homedir = os.environ["APPDATA"]

    # Otherwise, install in the user's home directory.
    else:
        homedir = os.path.expanduser("~/")
        if homedir == "~/":
            raise ValueError("Could not find a default download directory")

    # append "nltk_data" to the home directory
    return os.path.join(homedir, "aitool_data")


class DownloadMethod(Enum):
    urlretrieve = 1
    get = 2


def _report_process(block_num, block_size, total_size):
    sys.stdout.write('\r>> Downloading %.1f%%' % (float(block_num * block_size) / float(total_size) * 100.0))
    sys.stdout.flush()


def download_file(
        url: str,
        filename: str,
        method: DownloadMethod = DownloadMethod.urlretrieve,
        reporthook: Callable = _report_process,     # for DownloadMethod.urlretrieve
        data: Any = None,                           # for DownloadMethod.urlretrieve
        show: bool = True,                          # for DownloadMethod.urlretrieve
) -> str:
    try:
        if show:
            print("Start downloading {} to {}...".format(url, filename))
        if method == DownloadMethod.urlretrieve:
            request.urlretrieve(url, filename, reporthook, data)
        elif method == DownloadMethod.get:
            chunk_size = 1024
            make_dir(filename)
            resp = requests.get(url, stream=True)
            content_size = math.ceil(int(resp.headers['Content-Length']) / chunk_size)
            with open(filename, "wb") as file:
                for data in tqdm(iterable=resp.iter_content(1024), total=content_size, unit='k', desc=filename):
                    file.write(data)
        if show:
            print("Download {} successfully!".format(url))
    except (error.HTTPError, error.URLError) as e:
        print(e)
    return filename

def get_aitool_data_path(
        file_name,
        url_root=WEBPATH,
        packed: bool = False,
        packed_name=None,
        pack_way=None,
):
    # 目前仅支持在aitool_data目录下直接放文件，如果有文件夹无法处理
    file_dir = get_download_dir()
    file_path = os.path.join(file_dir, file_name)
    if is_file_exist(file_path):
        return file_path
    if not url_root:
        raise ValueError("invalid url_root")
    # 不是压缩包
    if not packed:
        url = os.path.join(url_root, file_name)
        download_file(url, file_path, method=DownloadMethod.get, show=False)
    # 是压缩包 (文件名不同，可能有多级路径)
    else:
        url = os.path.join(url_root, packed_name)
        pack_path = os.path.join(file_dir, packed_name)
        download_file(url, pack_path, method=DownloadMethod.get, show=False)
        # TODO 默认用zip解压，未考虑其他压缩格式
        if not pack_way:
            unzip(pack_path, file_dir)
    if is_file_exist(file_path):
        return file_path
    else:
        raise ValueError("not find: {}".format(file_name))


def prepare_data(url: str, directory: str = '', packed: bool = False, pack_way: str = '', tmp_dir: str = '') -> NoReturn:
    warnings.warn("推荐使用get_aitool_data_path", DeprecationWarning)
    if not packed:
        download_file(url, directory)
    else:
        if not tmp_dir:
            from aitool.datasets import PATH as DATA_PATH
            tmp_dir = os.path.join(DATA_PATH, 'tmp')
        packed_file = download_file(url, tmp_dir)
        unzip(packed_file, directory)


if __name__ == '__main__':
    print(get_download_dir())
    # link = 'https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png'
    # download_file(link, './x.jpg', method=DownloadMethod.get, show=False)
