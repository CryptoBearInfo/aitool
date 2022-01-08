# 便捷地实现多进程

假如函数toy需要被多次调用：
```python
def toy(x, y=1):
    sleep(random())
    return x, y
```

假设之前是这样调用的：
```python
for i in range(3):
    print(toy(i))
```

要改成多进程执行，只需要这么写。[按序执行、原生方法、multi方法的对比](#按序执行、原生方法、multi方法的对比)：
```python
# 获取所有要执行的函数
functions = get_functions(toy, range(3))
# 多进程执行
for result in multi(functions):
    print(result)
```


### How To Use

- [环境配置](#环境配置)
- [multi基本用法](#multi基本用法)
- [multi按序输出](#multi按序输出)
- [get_functions基本用法](#get_functions基本用法)
- [get_functions通常用法](#get_functions通常用法)
- [multi通常用法](#multi通常用法)
- [按序执行、原生方法、multi方法的对比](#按序执行、原生方法、multi方法的对比)

### 环境配置
```shell script
pip install aitool
```

### multi基本用法
- 由于是多进程，输出顺序不固定

```python
from time import sleep
from random import random
from aitool import multi


def toy_1(x=1, y=2):
    sleep(random())
    return x, y


def toy_2(x=3, y=4):
    sleep(random())
    return x, y


for result in multi([toy_1, toy_2]):
    print(result)
```
> 输出
```text
(3, 4)
(1, 2)
```

### multi按序输出
- 如果需要输出保持原有顺序，只需要设置`ordered=True`。
- 输出一定是按序的

```python
from time import sleep
from random import random
from aitool import multi


def toy_1(x=1, y=2):
    sleep(random())
    return x, y


def toy_2(x=3, y=4):
    sleep(random())
    return x, y


for result in multi([toy_1, toy_2], ordered=True):
    print(result)
```
> 输出
```text
(1, 2)
(3, 4)
```

### get_functions基本用法
- 需要并发执行的往往是同一个函数，只不过参数不一样。  
- get_functions可以基于参数列表生成函数列表。

```python
from time import sleep
from random import random
from aitool import get_functions


def toy(x):
    sleep(random())
    return x


for function in get_functions(toy, range(3)):
    print(function())
```
> 输出
```text
0
1
2
```

### get_functions通常用法
- 支持多种灵活的传参方式

```python
from time import sleep
from random import random
from aitool import get_functions


def toy(x, y=1):
    sleep(random())
    return x, y


condition = [1, [2, 3], {'x': 4}, {'x': 6, 'y': 7}]
for function in get_functions(toy, condition):
    print(function())
```
> 输出
```text
(1, 1)
(2, 3)
(4, 1)
(6, 7)
```

### multi通常用法
- 先用get_functions获取函数列表  
- 再用multi多进程执行

```python
from time import sleep
from random import random
from aitool import get_functions, multi


def toy(x, y=1):
    sleep(random())
    return x, y


condition = [1, [2, 3], {'x': 4}, {'x': 6, 'y': 7}]
functions = list(get_functions(toy, condition))
for result in multi(functions):
    print(result)
```
> 输出
```text
(2, 3)
(6, 7)
(4, 1)
(1, 1)
```


### 按序执行、原生方法、multi方法的对比
> 测试环境: 16核mac笔记本电脑, 可能会有一些误差
> 需要先安装环境`pip install aitool`

| 函数名 | 细节 | 改动量 | 耗时（秒） |
| --- | --- | --- | --- |
| test_sequence() | 按顺序执行多次toy函数 | - | 4981.669 |
| test_use_pool() | 用multiprocess实现 | 需改写12行代码 | 420.896 |
| test_use_multi() | 用multi实现 | 需改写2行代码 | 420.262 |
| test_use_multi(ordered=True) | 用multi实现，并按序输出 | 需改写2行代码 | 419.933 |

```python
from os import cpu_count
from random import random
from time import sleep
import multiprocess as mp
from aitool import get_functions, multi, exe_time


SLEEP_TIME = [random() for _ in range(10000)]


def toy(x):
    sleep(x)
    return x


def do_something_in_parent_process(data):
    print(data)


@exe_time(print_time=True)
def test_sequence():
    data = [toy(time) for time in SLEEP_TIME]
    do_something_in_parent_process(data)


@exe_time(print_time=True)
def test_use_pool():
    def toy_4_multiprocess(x, _queue):
        sleep(random())
        _queue.put(x)

    queue = mp.Manager().Queue()
    pool = mp.Pool(processes=cpu_count())
    for time in SLEEP_TIME:
        pool.apply_async(toy_4_multiprocess, args=(time, queue,))
    pool.close()
    pool.join()
    data = []
    while not queue.empty():
        data.append(queue.get(False))
    do_something_in_parent_process(data)


@exe_time(print_time=True)
def test_use_multi(ordered=False):
    functions = list(get_functions(toy, SLEEP_TIME))
    data = [result for result in multi(functions, ordered=ordered)]
    do_something_in_parent_process(data)


test_use_pool()
test_use_multi()
test_use_multi(ordered=True)
test_sequence()
```