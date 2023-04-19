# -*- coding: UTF-8 -*-
# @Time    : 2021/3/10
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
import time


def exe_time(print_time=False, print_key=None, detail=False, get_time=False):
    def wrapper(func):
        def decorate(*args, **kw):
            t0 = time.time()
            if detail:
                print("@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__))
            back = func(*args, **kw)
            if detail:
                print("@%s, {%s} finish" % (time.strftime("%X", time.localtime()), func.__name__))
            time_dif = time.time() - t0
            # print_key设置后，会依据其值来修改print_time的值
            # TODO 默认值取不到，即必须在调用函数时指定参数后才能取到
            do_print = print_time
            if print_key is not None:
                if isinstance(print_key, str) and print_key in kw and isinstance(kw[print_key], bool):
                    do_print = kw[print_key]
            if do_print:
                print("@%.3fs taken for {%s}" % (time_dif, func.__name__))
            if get_time:
                return back, time_dif
            return back
        return decorate
    return wrapper


if __name__ == '__main__':
    @exe_time()
    def test1():
        print('test1')


    @exe_time(print_time=True)
    def test2():
        print('test2')


    @exe_time(detail=True)
    def test3():
        print('test3')


    @exe_time(get_time=True)
    def test4():
        print('test4')
        return 'hello'


    @exe_time(print_time=True, print_key='show')
    def test5(show=False):
        print(show)
        print('test5')


    test1()
    test2()
    test3()
    print(test4())
    test5(show=False)
    test5(show=True)
