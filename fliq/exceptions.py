class BaseQueryException(Exception):
    pass


class MultipleItemsFoundException(BaseQueryException):
    pass


class NoItemsFoundException(BaseQueryException):
    pass


class NotEnoughElementsException(BaseQueryException):
    pass
