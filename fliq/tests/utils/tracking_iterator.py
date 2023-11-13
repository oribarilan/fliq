class TrackingIterator:
    def __init__(self, iterable):
        self.iterable = iter(iterable)
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        return next(self.iterable)
