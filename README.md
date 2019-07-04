## tok

[![PyPI](https://img.shields.io/pypi/v/tok.svg?style=flat-square)](https://pypi.python.org/pypi/tok/)
[![PyPI](https://img.shields.io/pypi/pyversions/tok.svg?style=flat-square)](https://pypi.python.org/pypi/tok/)

Fastest and most complete/customizable tokenizer in Python.

Roughly 25x faster than spacy's and nltk's regex based tokenizers.

### Installation

    pip install tok

It depends on [textsearch](https://github.com/kootenpv/textsearch).

### Usage

By default it handles contractions, http, (float) numbers and currencies.

```python
from tok import word_tokenize
word_tokenize("I wouldn't do that.... would you?")
['I', 'would', 'not', 'do', 'that', '...', 'would', 'you', '?']
```

Or configure it yourself:

```python
from tok import Tokenizer
tokenizer = Tokenizer(protected_words=["some.thing"]) # still using the defaults
tokenizer.word_tokenize("I want to protect some.thing")
['I', 'want', 'to', 'protect', 'some.thing']
```

Split by sentences:

```python
from tok import sent_tokenize
sent_tokenize("I wouldn't do that.... would you?")
[['I', 'would', 'not', 'do', 'that', '...'], ['would', 'you', '?']]
```

for more options check the documentation of the `Tokenizer`.

### Further customization

Given:

```python
from tok import Tokenizer
t = Tokenizer(protected_words=["some.thing"]) # still using the defaults
```

You can add your own ideas to the tokenizer by using:

- `t.keep(x, reason)`: Whenever it finds x, it will not add whitespace. Prevents direct tokenization.
- `t.split(x, reason)`: Whenever it finds x, it will surround it by whitespace, thus creating a token.
- `t.drop(x, reason)`: Whenever it finds x, it will remove it but add a split.
- `t.strip(x, reason)`: Whenever it finds x, it will remove it without splitting.

```python
tokenizer.drop("bla", "bla is not needed")
t.word_tokenize("Please remove bla, thank you")
['Please', 'remove', ',', 'thank', 'you']
```

### Explainable

Explain what happened:

```python
t.explain("bla")
[{'from': 'bla', 'to': ' ', 'explanation': 'bla is not needed'}]
```

See everything in there (will help you understand how it works):

```python
t.explain_dict
```

### Contributing

It would be greatly appreciated if you want to contribute to this library.

It would also be great to add [contractions](https://github.com/kootenpv/contractions) for other languages.
