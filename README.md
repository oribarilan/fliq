#  <img src="assets/flick_emoji_2_small.png" alt="drawing" width="40" height="40"/> Fliq

Fluent-syntax Lazily-evaluated Integrated Query.

Fluent is:

- **Readable & Easy**: Designed for readability and ease of use. Using fluent syntax.
- **Lightweight**: Thin wrapper for the standard library. No dependencies.
- **Performant**: On-par with the standard library. 
Abstraction overhead is kept to a minimum, keeping CPython performance. 
- **Lazy**: All operations are lazy, and only evaluated when needed. 
This provides a performance boost for cases where user would have used list-comprehension otherwise.
- **Compatible**: Compatible with APIs consuming iterables.