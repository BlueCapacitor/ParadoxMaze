from timeit import timeit

from tools.template import Template
from tools.table import Table


def dev_test():
    time_test()

    table = Table([
        Template()[0],
        Template()[1],
        Template()[2]
    ])

    for a in range(4):
        for b in range(4):
            for c in range(4):
                table.append((a, b, c))

    print(table[Template()[0]])


def time_test():
    table = Table([
        Template()[0],
        Template()[1],
        Template()[2],
        (Template()[0], Template()[1])
    ])
    for a in range(100):
        for b in range(100):
            for c in range(10):
                table.append((a, b, c))

    def f1():
        return list(table[(Template()[0], Template()[1]), (1, 2)])

    def f2():
        return list(filter(lambda tup: tup[0] == 1 and tup[1] == 2, table.items))

    print(f1())
    print(f2())

    print()

    print(timeit(f1, number=1000))
    print(timeit(f2, number=1000))
