from typing import Callable, Any, Union

Predicate = Callable[[Any], bool]
Selector = Callable[[Any], Any]
NumericSelector = Callable[[Any], Union[int, float]]
IndexSelector = Callable[[Any], int]
