# -*- coding: UTF-8 -*-
# @Time    : 2020/10/26
# @Author  : xiangyuejia@qq.com
from typing import Any, List


class Node:
    """
    The *Node* in the graph must have a *name* and can have an additional *info* of any structure.
    The *name* and *info* must support the **=** operation.
    *name* is not the identifier of *Node*.
    图谱中的节点*Node*必须有一个*name*，并可以带有一个额外的任意结构的*info*。
    *name*和*info*必须支持**=**操作。
    *name*并不是*Node*的标识符。
    """
    def __init__(self, name: Any, info: Any = None) -> None:
        self.name = name
        self.info = info


class Edge:
    def __init__(self, end: int, pre: int, name: Any = None,info: Any = None) -> None:
        self.end = end
        self.pre = pre
        self.name = name
        self.info = info


class Piece:
    def __init__(
            self,
            node_begin: Any,
            node_end: Any,
            relation: Any,
            node_begin_info: Any = None,
            node_end_info: Any = None,
            relation_info: Any = None,
    ):
        self.node_begin = node_begin
        self.node_end = node_end
        self.relation = relation
        self.node_begin_info = node_begin_info
        self.node_end_info = node_end_info
        self.relation_info = relation_info


def reform_data(data: List[Any]) -> List[Piece]:
    reformed_data = []
    for d in data:
        if isinstance(d, list):
            if len(d) == 3:
                reformed_data.append(Piece(d[0], d[2], d[1]))
            elif len(d) == 6:
                reformed_data.append(Piece(d[0], d[2], d[1], d[3], d[5], d[4]))
            else:
                raise ValueError
        if isinstance(d, dict):
            if 'node_begin' not in d: raise ValueError
            if 'node_end' not in d: raise ValueError
            if 'relation' not in d: raise ValueError
            if 'node_begin_info' not in d: d['node_begin_info'] = None
            if 'node_end_info' not in d: d['node_end_info'] = None
            if 'relation_info' not in d: d['relation_info'] = None
            reformed_data.append(Piece(d['node_begin'], d['node_end'], d['relation'],
                                       d['node_begin_info'], d['node_end_info'], d['relation_info']))
    return reformed_data


class ChainForwardStars:
    def __init__(self) -> None:
        self.node_name2index: map = {}
        self.index2node_name: map = {}
        self.heads: list = []
        self.nodes: list = []
        self.edges: list = []
        self.node_count: int = 0
        self.edge_count: int = 0

    def get_node_index(self, node_name: int or str, info: Any = None) -> int:
        if node_name in self.node_name2index:
            for index in self.node_name2index[node_name]:
                if self.nodes[index].info == info:
                    return index
            return self.node_name2index[node_name]
        new_node = Node(node_name, info=info)

        if node_name in self.node_name2index:
            self.node_name2index[node_name].append(self.node_count)
        else:
            self.node_name2index[node_name] = [self.node_count]
        self.index2node_name[self.node_count] = node_name
        self.nodes.append(new_node)
        index = self.node_count
        self.node_count += 1
        self.heads.append(-1)
        return index

    def add_triple(
            self,
            node_begin_name: Any,
            node_end_name: Any,
            relation_name: Any,
            node_begin_info: Any = None,
            node_end_info: Any = None,
            relation_info: Any = None,
    ) -> None:
        index_begin = self.get_node_index(node_begin_name, info=node_begin_info)
        index_end = self.get_node_index(node_end_name, info=node_end_info)

        edge = Edge(index_end, self.heads[index_begin], name=relation_name, info=relation_info)
        self.edges.append(edge)
        self.heads[index_begin] = self.edge_count
        self.edge_count += 1

    def built(self, data: list) -> None:
        # for e1, r, e2 in data:
        #     self.add_triple(e1, e2, r)
        for piece in data:
            self.add_triple(
                piece.node_begin,
                piece.node_end,
                piece.relation,
                piece.node_begin_info,
                piece.node_end_info,
                piece.relation_info
            )

    def print(self) -> str:
        out_print = ''
        for i in range(self.node_count):
            out_print += ' #{}'.format(self.index2node_name[i])
            p = self.heads[i]
            while p != -1:
                out_print += '->{}'.format(self.index2node_name[self.edges[p].end])
                p = self.edges[p].pre
        return out_print.lstrip()

    def clear(self):
        self.__init__()


if __name__ == '__main__':
    test_case_1 = [
        [1, '1', 2],
        [2, '2', 3],
        [3, '3', 4],
        [1, '4', 3],
        [4, '5', 1],
        [1, '6', 5],
        [4, '7', 5],
        ]

    test_case_2 = [
        ['n1', 'r1', 'n2', {'kind': 'dis'}, {'kind': 'sim', 'weight': 0.92}, {'kind': 'dis'}],
        ['n2', 'r3', 'n4', {'kind': 'dis'}, {'kind': 'dif'}, {'kind': 'dis'}],
        ['n2', 'r2', 'n3', {'kind': 'dis'}, {'kind': 'has'}, {'kind': 'ato'}],
        ['n1', 'r4', 'n4', {'kind': 'dis'}, {'kind': 'dif'}, {'kind': 'dis'}],
    ]

    test_case_3 = [
        {'node_begin':1, 'node_end':2, 'relation':1},
        {'node_begin':2, 'node_end':3, 'relation':2},
        {'node_begin':3, 'node_end':4, 'relation':3},
        {'node_begin':1, 'node_end':3, 'relation':4},
        {'node_begin':4, 'node_end':1, 'relation':5},
        {'node_begin':1, 'node_end':5, 'relation':6},
        {'node_begin':4, 'node_end':5, 'relation':7},
    ]

    cfs = ChainForwardStars()
    cfs.built(reform_data(test_case_1))
    assert cfs.print() == '#1->5->3->2 #2->3 #3->4 #4->5->1 #5'
    print('ChainForwardStars has passed the unit test: test_case_1.')

    cfs.clear()
    cfs.built(reform_data(test_case_2))
    assert cfs.print() == '#n1->n4->n2 #n2->n3->n4 #n4 #n3'
    print('ChainForwardStars has passed the unit test: test_case_2.')

    cfs.clear()
    cfs.built(reform_data(test_case_3))
    assert cfs.print() == '#1->5->3->2 #2->3 #3->4 #4->5->1 #5'
    print('ChainForwardStars has passed the unit test: test_case_3.')
