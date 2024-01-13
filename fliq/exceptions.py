class BaseQueryException(Exception):
    pass


class MultipleElementsFoundException(BaseQueryException):
    pass


class QueryIsUnexpectedlyEmptyException(BaseQueryException):
    pass


class NotEnoughElementsException(BaseQueryException):
    pass


class ElementNotFoundException(BaseQueryException):
    pass

