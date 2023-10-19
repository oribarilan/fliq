from typing import Callable, Any

Predicate = Callable[[Any], bool]
Selector = Callable[[Any], Any]
