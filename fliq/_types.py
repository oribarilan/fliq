from typing import TypeVar, Union, Optional, Callable


class Missing:
    # sentinel class to represent a parameter that was not passed to a method
    pass


T = TypeVar('T')
U = TypeVar('U')

MissingOr = Union[T, Missing]
MissingOrOptional = Union[Optional[T], Missing]
MISSING = Missing()

# editing of type aliases should also update api_intro.md
Predicate = Callable[[T], bool]
Selector = Callable[[T], U]

NumericSelector = Selector[T, Union[int, float]]
IndexSelector = Selector[T, int]
