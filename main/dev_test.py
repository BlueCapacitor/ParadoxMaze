from timeit import timeit

from tools.template import Template, template
from tools.table import Table


def dev_test():
    table = Table([],
                  (Table.reduce_max(template[0]),
                   Table.reduce_any(template[1]),
                   Table.reduce_sum(template[0])))
    print(table.reduce(*Table.reduce_max(template[0])),
          table.reduce(*Table.reduce_any(template[1])),
          table.reduce(*Table.reduce_sum(template[0])))
    table.append((3, False))
    print(table.reduce(*Table.reduce_max(template[0])),
          table.reduce(*Table.reduce_any(template[1])),
          table.reduce(*Table.reduce_sum(template[0])))
    table.append((5, False))
    print(table.reduce(*Table.reduce_max(template[0])),
          table.reduce(*Table.reduce_any(template[1])),
          table.reduce(*Table.reduce_sum(template[0])))
    table.append((-1, True))
    print(table.reduce(*Table.reduce_max(template[0])),
          table.reduce(*Table.reduce_any(template[1])),
          table.reduce(*Table.reduce_sum(template[0])))
    table.append((0, False))
    print(table.reduce(*Table.reduce_max(template[0])),
          table.reduce(*Table.reduce_any(template[1])),
          table.reduce(*Table.reduce_sum(template[0])))


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
