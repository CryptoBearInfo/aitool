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
import os
from aitool import print_green
from typing import Dict, Union, List, Any, NoReturn, Tuple


def pip_install_by_os(package_name: str) -> bool:
    # requests && rm -rf *
    if '-r' in package_name or '&&' in package_name or '*' in package_name:
        return False
    os.system('pip install {}'.format(package_name))
    return True


def pip_install_by_main(package_name: str) -> bool:
    try:
        from pip import main
    except Exception as e:
        print(e)
        return False
    main(['install', '{}'.format(package_name)])


def pip_install(package_name: str) -> bool:
    print_green('lazy install package {}'.format(package_name))
    if '--' not in package_name:
        # 简单的直接用包名+版本号的格式
        try:
            return pip_install_by_main(package_name)
        except Exception as e:
            print(e)
    try:
        # 复杂的格式
        return pip_install_by_os(package_name)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    pip_install('jieba')
    pip_install('jieba==0.42.1')
    pip_install('networkx >= 2.6.3')
