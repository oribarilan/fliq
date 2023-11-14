# Examples

## Tonny's Socks 🧦

Tonny is terrible at doing laundry. He has a drawer full of socks, but none of them match. 
He needs to find a pair of matching socks before he can go to work.
Also, it is Christmas, so preferably something in the holiday spirit.

```python
from fliq import q
from dataclasses import dataclass

@dataclass
class Sock:
    color: str
    foot: str

sock_drawer = [
    Sock('red', 'left'), Sock('green', 'left'), Sock('burgers', 'left'), Sock('aliens', 'right'),
    Sock('avocados', 'left'), Sock('avocados', 'right'), Sock('red', 'right'), Sock('burgers', 'left')
]

# split socks into singles and pairs
singles, pairs = q(sock_drawer).group_by('color').partition(by=lambda g: len(g) == 2)

# put singles back in the drawer
sock_drawer = singles.flatten().to_list()

# find a pair of red socks or default to boring black
pair = pairs.first_or_default(lambda p: p[0].color == 'red', default=(Sock('boring black', 'left'), Sock('boring black', 'right')))

print(f"Tonny's socks for today are {pair[0].color}! 🎄🎅🏼🎁🧦🧦🎁🎅🏼🎄")
```

## Language Contest 👨‍💻🏆
Let's find out which programming language is the most popular.

### The Easy Way

```python
from fliq import q

languages = ['Python', 'JavaScript', 'C#', 'Java', 'C++', 'C']
popular_languages = q(languages).order(by=lambda l: len(l), ascending=False).to_list()

print(f"Here are the most popular programming languages: {popular_languages} 😅")

# ['JavaScript', 'Python', 'C++', 'Java', 'C#', 'C']
```

### The Hard Way

We'll use the [GitHub API](https://docs.github.com/en/free-pro-team@latest/rest) to get the top 100 repos by stars,
and then count the appearances of each language.

```python
import requests
from collections import Counter
from fliq import q

# get the top 100 repos by stars
repos = requests.get('https://api.github.com/search/repositories?q=stars:>1&sort=stars&per_page=100').json()['items']

# get the language for each repo
languages = q(repos).select(lambda r: r['language'])

# peek to see a language, without removing it from the query
peeked_language = languages.peek()

print(f"Here's a peek at the languages: {peeked_language}")

# count popularity of each language
popular_languages = Counter(languages).most_common()
print(f"Here are the most popular programming languages: {popular_languages} 💪🧪🔍")

# [('JavaScript', 16), ('TypeScript', 15), ('Python', 13), (None, 13), ('C', 5), ('Java', 5) ...]
```
