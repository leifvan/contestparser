from typing import Any, Iterable, Callable, Generator, List
from functools import partial


class Node:
    def __init__(self, value: Any):
        self.is_leaf = True
        self.value = value

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


class Parser:
    """
    A parser that interprets the input as a tree that can be expanded, mapped and reduced.
    """

    def __init__(self, input):
        """
        Creates a parser with one leaf `input`.
        :param input: The value of the initial leaf.
        """
        self.tree = Node(input)

    def expand(self, func: Callable[[Any], Iterable]) -> 'Parser':
        """
        Applies ``func`` to every leaf of the tree and replaces the leaf with an inner node. It
        generates leaves for this inner node by iterating over the return value of ``func``.

        This method increases the height of the tree by 1.
        """
        for leaf in self.tree.leaves():
            leaf.is_leaf = False
            leaf.value = [Node(s) for s in func(leaf.value)]
        return self

    def map(self, func: Callable[[Any], Any]) -> 'Parser':
        """
        Applies ``func`` to every leaf and replaces it's old value with the return value
        of ``func``.

        This method does not change the height of the tree.
        """
        for leaf in self.tree.leaves():
            leaf.value = func(leaf.value)
        return self

    def reduce(self, func: Callable[[Iterable], Any]) -> 'Parser':
        """
        Calls ``func`` with an iterable over all children of a lowest inner node (i.e. children
        with a common parent node) and replaces that node with a leaf containing the value returned
        by ``func``.

        This method decreases the height of the tree by 1.
        """
        for node in self.tree.lowest_nodes():
            node.value = func([leaf.value for leaf in node.value])
            node.is_leaf = True
        return self

    def get(self) -> Any:
        """
        Returns the value of the root node if it is a leaf.
        """
        if self.tree.is_leaf:
            return self.tree.value
        raise Exception("Can't get value if root is not a leaf.")

    def split(self, separator: str) -> 'Parser':
        """
        A convenience method that calls ``split(separator)`` of the values of all leaves and
        expanding them.
        """
        return self.expand(lambda value: value.split(separator))

    def to_list(self) -> List:
        """
        A convenience method that reduces the tree to a list of lists by converting lowest inner
        nodes to leaves with a list of their children's values until only a single leaf remains.
        :return: The list contained in the single leaf node.
        """
        while not self.tree.is_leaf:
            self.reduce(list)
        return self.get()


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

    p = Parser(text).split('\n').split(' ').reduce('_'.join).reduce(' -> \n'.join)
    result = p.get()
    print(result)
