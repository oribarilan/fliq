from numbers import Number
from typing import Callable, Any

Predicate = Callable[[Any], bool]
Selector = Callable[[Any], Any]
NumericSelector = Callable[[Any], Number]
