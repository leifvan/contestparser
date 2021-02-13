from typing import Any, Iterable, Callable, Generator, List, NamedTuple
from functools import partial


class Node:
    def __init__(self, value: Any, parent: 'Node' = None):
        self.is_leaf = True
        self.value = value
        self.parent = parent

    def __getitem__(self, item: int) -> Any:
        if self.is_leaf:
            raise Exception("Can't iterate over a leaf.")
        return self.value[item]

    def leaves(self) -> Generator:
        if self.is_leaf:
            yield self
        else:
            for node in self:
                yield from node.leaves()

    def lowest_nodes(self) -> Generator:
        if self.is_leaf:
            raise Exception("Tree only consists of one node.")
        else:
            if self[0].is_leaf:  # this assumes that the tree is structurally homogeneous
                yield self
            else:
                for tree in self:
                    yield from tree.lowest_nodes()


def _expand_op(leaves, func):
    for leaf in leaves:
        yield from (Node(l, leaf) for l in func(leaf.value))


def _map_op(leaves, func):
    for leaf in leaves:
        yield Node(func(leaf.value), leaf.parent)


def _reduce_op(leaves, func):
    cur_parent = collected = None

    for leaf in leaves:
        if leaf.parent is not cur_parent:
            if cur_parent is not None:
                yield Node(func(collected), cur_parent.parent)
            cur_parent = leaf.parent
            collected = []

        collected.append(leaf.value)

    yield Node(func(collected), cur_parent.parent)


def _aggregate_op(leaves, func, init, init_factory):
    cur_parent = None
    cur_aggregate = None

    if init_factory is None:
        init_factory = lambda: init

    for leaf in leaves:
        if leaf.parent is not cur_parent:
            if cur_parent is not None:
                yield Node(cur_aggregate, cur_parent.parent)
            cur_parent = leaf.parent
            cur_aggregate = init_factory()

        if cur_aggregate is None:
            cur_aggregate = leaf.value
        else:
            cur_aggregate = func(cur_aggregate, leaf.value)

    yield Node(cur_aggregate, cur_parent.parent)


class TreeParser:
    """
    A parser that interprets the input as a tree that can be expanded, mapped and reduced.
    """

    def __init__(self, *inputs):
        """
        Creates a parser with one leaf `input`.
        :param input: The value of the initial leaf.
        """
        self.last_operation = (Node(inp) for inp in inputs)

    def expand(self, func: Callable[[Any], Iterable]) -> 'TreeParser':
        """
        Applies ``func`` to every leaf of the tree and replaces the leaf with an inner node. It
        generates leaves for this inner node by iterating over the return value of ``func``.
        """
        self.last_operation = _expand_op(self.last_operation, func)
        return self

    def map(self, func: Callable[[Any], Any]) -> 'TreeParser':
        """
        Applies ``func`` to every leaf and replaces it's old value with the return value
        of ``func``.
        """
        self.last_operation = _map_op(self.last_operation, func)
        return self

    def reduce(self, func: Callable[[Iterable], Any]) -> 'TreeParser':
        """
        Calls ``func`` with an iterable over all children of a lowest inner node (i.e. children
        with a common parent node) and replaces that node with a leaf containing the value returned
        by ``func``.

        Example: Given lowest inner nodes ``[[1,2,3,4], [5,6,7], [8,9]]``, the reduce operation
        results in ``[func([1,2,3,4]), func([5,6,7]), func([8,9])]``.
        """
        self.last_operation = _reduce_op(self.last_operation, func)
        return self

    def aggregate(self, func: Callable[[Any, Any], Any], init=None, init_factory=None) -> 'TreeParser':
        """
        Similar to ``reduce`` but instead of calling ``func`` with all children, it creates an
        aggregate by applying a binary function ``func`` successively with the intermediate
        aggregate and the next child value.

        Handling of the initial aggregate can be controlled by
        the ``init`` and ``init_factory`` parameters. If ``init`` is not ``None``, this value will
        be passed as the first aggregate. If ``init_factory`` is not ``None``, it will be called and
        the return value will be used as the first aggregate. If both parameters are ``None``, the
        first call to func will be done with the values of the first two leaves.

        Example: Given lowest inner nodes ``[[1,2,3,4], [5,6,7]]``, the aggregate operation (without
        special initialization) results in ``[func(func(func(1,2),3),4), func(func(5,6),7)]``.
        """
        self.last_operation = _aggregate_op(self.last_operation, func, init, init_factory)
        return self

    def get(self) -> Any:
        """
        Returns the value of the unique leaf of the tree. Raises an exception of there are multiple
        leaves.
        """
        # try to collapse the structure into one value
        result = list(self.last_operation)

        if len(result) > 1:
            raise Exception("Can't get value if root is not a leaf.")

        return result[0].value

    def leaves(self) -> Generator:
        """
        Returns a generator over all values of the leaves.
        """
        yield from (leaf.value for leaf in self.last_operation)

    def split(self, separator: str) -> 'TreeParser':
        """
        A convenience method that calls ``split(separator)`` of the values of all leaves and
        expanding them.
        """
        return self.expand(lambda value: value.split(separator))

    @classmethod
    def from_file(cls, file):
        """
        A convenience method that creates a parser initialized with the lines of the given file.
        """

        def line_generator():
            while line := file.readline():
                yield line

        return cls(*line_generator())


class ContestParser:
    def __init__(self):
        ...


if __name__ == '__main__':
    text = "Good evening is this available\n" \
           "Yes it is\n" \
           "Please leave me alone\n" \
           "we are sleeping\n" \
           "No more contacting please\n" \
           "Thanks appreciate\n" \
           "You contacted me\n" \
           "I know i no longer interested\n" \
           "Please stop contacting me now\n" \
           "I will contact attorney general\n" \
           "If you do not stop\n" \
           "Thsnks"

    p = (TreeParser(text)
         .split('\n')
         .split(' ')
         .aggregate(lambda a, b: a + '_' + b)
         .aggregate(lambda a, b: a + ' -> \n' + b))
    result = p.get()
    print(result)

    with open('testdata/huge.txt', 'r') as file:
        p = (TreeParser.from_file(file)
             .map(lambda line: line.strip())
             .split(' ')
             .reduce('_'.join))

        for i, leaf in enumerate(p.leaves()):
            if i % 10000 == 0:
                print(i, "|", leaf)
