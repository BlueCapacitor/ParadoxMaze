from collections import defaultdict
from collections.abc import Collection

from tools.template import Template


class Table(Collection):
    def __init__(self, dimensions, reduce_tuples=(), items=None, dimension_functions=None, dicts=None):
        self.dimensions = dimensions

        if dicts is None:
            self.dimension_functions = [Table.as_dimension_function(dimension) for dimension in dimensions]

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

    @staticmethod
    def as_dimension_function(dimension):
        return (lambda value: tuple(sub_dimension.replicate(value) for sub_dimension in dimension)) \
            if isinstance(dimension, tuple) else dimension.replicate

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

        for i, ((reduce_template, initial_val), cumulative) in enumerate(self.reduce_tuples):
            self.reduce_tuples[i] = [(reduce_template, initial_val),
                                     reduce_template.replicate(new=item, cumulative=cumulative)]

    def reduce(self, template, initial_val):
        for (test_template, test_initial_val), cumulative in self.reduce_tuples:
            if Template.is_equivalent(template, test_template) and \
                    Template.is_equivalent(initial_val, test_initial_val):
                return cumulative
        raise ValueError(f"({Template.template_str(template)}, {initial_val}) "
                         f"was not explicitly listed as a reduce dimension on table creation")

    @staticmethod
    def is_equivalent_dimension(dimension1, dimension2):
        match dimension1, dimension2:
            case tuple(), tuple():
                return all(Template.is_equivalent(*sub_dimensions) for sub_dimensions in zip(dimension1, dimension2))
            case Template(), Template():
                return Template.is_equivalent(dimension1, dimension2)
            case tuple((Template(),)), Template():
                return Template.is_equivalent(dimension1[0], dimension2)
            case Template(), tuple((Template(), )):
                return Template.is_equivalent(dimension2[0], dimension1)

    def copy(self):
        return Table(self.dimensions, list(map(list, self.reduce_tuples)), list(self.items), self.dimension_functions,
                     list(defaultdict(list, old) for old in self.dicts))

    @staticmethod
    def reduce_min(template):
        subst = Template.substitute(template, Template("new"))
        return Template.switch(Template.is_(Template("cumulative"), None),
                               Template.min(subst, Template("cumulative")), subst), None

    @staticmethod
    def reduce_max(template):
        subst = Template.substitute(template, Template("new"))
        return Template.switch(Template.is_(Template("cumulative"), None),
                               Template.max(subst, Template("cumulative")), subst), None

    @staticmethod
    def reduce_sum(template, start=0):
        subst = Template.substitute(template, Template("new"))
        return Template("cumulative") + subst, start

    @staticmethod
    def reduce_prod(template, start=1):
        subst = Template.substitute(template, Template("new"))
        return Template("cumulative") * subst, start

    @staticmethod
    def reduce_any(template):
        subst = Template.substitute(template, Template("new"))
        return Template.or_(Template("cumulative"), subst), False

    @staticmethod
    def reduce_all(template):
        subst = Template.substitute(template, Template("new"))
        return Template.and_(Template("cumulative"), subst), True
