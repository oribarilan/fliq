from abc import ABC


class Queryable(ABC):

    # Carriers

    def all(self):
        pass

    def where(self, predicate):
        pass

    def select(self, selector):
        pass

    # Collectors

    def count(self):
        pass

    def first_or_default(self, predicate=None, default=None):
        pass

    def first(self, predicate=None):
        pass

    def get(self, predicate=None):
        pass
