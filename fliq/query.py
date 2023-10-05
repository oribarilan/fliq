from fliq.collector import Collector


class Query(Collector):
    def __iter__(self):
        return self.all()
