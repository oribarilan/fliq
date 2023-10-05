from fliq.collector import Collector
from fliq.queryable import Queryable


class Query(Collector, Queryable):
    def __iter__(self):
        return self.all()
