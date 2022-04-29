from collections import deque
from collections.abc import Iterator


class AllButLast(Iterator):
    class IteratorNotEmptyError(Exception):
        pass

    def __init__(self, source, buffer_size=1):
        self.source = source if isinstance(source, Iterator) else iter(source)
        self.empty = False

        try:
            self.buffer = deque(next(self.source) for _ in range(buffer_size))
        except StopIteration:
            raise StopIteration("Source iterator ran out of contents before the initial buffer was filled")

    def __next__(self):
        try:
            self.buffer.append(next(self.source))
            return self.buffer.popleft()
        except StopIteration:
            self.empty = True
            raise StopIteration

    @property
    def remaining(self):
        if self.empty:
            return self.buffer
        else:
            raise AllButLast.IteratorNotEmptyError("Can not get remaining items before the first items are collected")
