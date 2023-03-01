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
from aitool import make_dir
import requests
import os
import math
from enum import Enum
from tqdm import tqdm
# TODO 最基础的网络下载能力，后续download/utils里的修改为复用本文件里的方法


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
) -> None:
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


if __name__ == '__main__':
    link = 'https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png'
    download_file(link, './x.jpg', method=DownloadMethod.get, show=False)
