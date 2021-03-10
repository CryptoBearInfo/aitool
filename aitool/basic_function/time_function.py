# -*- coding: UTF-8 -*-
# @Time    : 2021/3/10
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import time

def exe_time(func, print_time=False):
    def new_func(*args, **args2):
        t0 = time.time()
        # print("@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__))
        back = func(*args, **args2)
        # print("@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__))
        if print_time:
            print("@%.3fs taken for {%s}" % (time.time() - t0, func.__name__))
        return back
    return new_func
