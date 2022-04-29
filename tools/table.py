from collections import defaultdict
from collections.abc import Collection
from typing import Any, Callable

from tools.template import Template


class Table(Collection):
    def __init__(self, dimensions, reduce_tuples=(), items=None, dimension_functions=None, dicts=None):
        self.dimensions = dimensions

        if dicts is None:
            self.dimension_functions = [
                (lambda value: tuple(sub_dimension.replicate(value) for sub_dimension in dimension))
                if isinstance(dimension, tuple) else dimension.replicate
                for dimension in dimensions]

            self.reduce_tuples = [[reduce_tuple, reduce_tuple[1]] for reduce_tuple in reduce_tuples]

            self.items = []
            self.dicts = [defaultdict(list) for _ in self.dimensions]

            if items is not None:
                for item in items:
                    self.append(item)
        else:
            self.dimension_functions = dimension_functions
            self.reduce_tuples = reduce_tuples
            self.items = items
            self.dicts = dicts

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, item):
        return item in self.items

    def __getitem__(self, args):
        match args:
            case dimension, value:
                return self.partition(dimension)[value]
            case index:
                if isinstance(index, (int, slice)):
                    return self.items[index]
                else:
                    return self.partition(index)

    def partition(self, dimension):
        return self.dicts[[Table.is_equivalent_dimension(potential_dimension, dimension)
                           for potential_dimension in self.dimensions].index(True)]

    def append(self, item):
        self.items.append(item)
        for i, dimension_dict in enumerate(self.dicts):
            dimension_dict[self.dimension_functions[i](item)].append(item)

        for i, ((reduce_func, initial_val), cumulative) in enumerate(self.reduce_tuples):
            self.reduce_tuples[i] = [(reduce_func, initial_val), reduce_func(item, cumulative)]

    def reduce(self, template, initial_val):
        for (test_template, test_initial_val), cumulative in self.reduce_tuples:
            if template.is_equivalent(test_template) and initial_val.is_equivalent(test_initial_val):
                return cumulative

    @staticmethod
    def is_equivalent_dimension(dimension1, dimension2):
        if isinstance(dimension1, tuple) and isinstance(dimension2, tuple):
            return all(sub_dimensions[0].isequivalent(sub_dimensions[1])
                       for sub_dimensions in zip(dimension1, dimension2))
        elif isinstance(dimension1, Template) and isinstance(dimension2, Template):
            return dimension1.is_equivalent(dimension2)
        else:
            return False

    def copy(self):
        return Table(self.dimensions, list(map(list, self.reduce_tuples)), list(self.items), self.dimension_functions,
                     list(defaultdict(list, old) for old in self.dicts))

    @staticmethod
    def template_to_func(template) -> Callable[[Any], Any]:
        return template.replicate if isinstance(template, Template) else template

    @staticmethod
    def reduce_min(template):
        func = Table.template_to_func(template)
        return (lambda new, cumulative: func(new) if cumulative is None else min(func(new), cumulative)), None

    @staticmethod
    def reduce_max(template):
        func = Table.template_to_func(template)
        return (lambda new, cumulative: func(new) if cumulative is None else max(func(new), cumulative)), None\


    @staticmethod
    def reduce_sum(template):
        func = Table.template_to_func(template)
        return (lambda new, cumulative: func(new) + cumulative), 0

    @staticmethod
    def reduce_prod(template):
        func = Table.template_to_func(template)
        return (lambda new, cumulative: func(new) * cumulative), 1

    @staticmethod
    def reduce_any(template):
        func = Table.template_to_func(template)
        return (lambda new, cumulative: func(new) or cumulative), False

    @staticmethod
    def reduce_all(template):
        func = Table.template_to_func(template)
        return (lambda new, cumulative: func(new) and cumulative), True
