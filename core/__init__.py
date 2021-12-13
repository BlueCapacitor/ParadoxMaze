class MultiIndex:
    def __init__(self, obj, factory):
        self.obj = obj
        self.factory = factory

    def __getitem__(self, slices):
        return self.factory(self.obj[s] for s in slices)
