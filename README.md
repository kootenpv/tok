## tok

[![PyPI](https://img.shields.io/pypi/v/tok.svg?style=flat-square)](https://pypi.python.org/pypi/tok/)
[![PyPI](https://img.shields.io/pypi/pyversions/tok.svg?style=flat-square)](https://pypi.python.org/pypi/tok/)

Fastest and most complete/customizable tokenizer in Python.

It is roughly 25x faster than spacy's and nltk's regex based tokenizers.

Using the aho-corasick algorithm makes it a novelty and allows it to be both explainable and fast in how it will split.

The heavy lifting is done by [textsearch](https://github.com/kootenpv/textsearch) and [pyahocorasick](https://github.com/WojciechMula/pyahocorasick), allowing this to be written in only ~200 lines of code.

Contrary to regex-based approaches, it will go over each character in a text only once. Read [below](#how-it-works) about how this works.

### Installation

    pip install tok

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

### How it works

It will always only keep the longest match. By introducing a space in your tokens, it will make it be split.

If you consider how the tokenization of `.` works, see here:

- When it finds a ` A.` it will make it ` A.` (single letter abbreviations)
- When it finds a `.0` it will make it `.0` (numbers)
- When it finds a `.`, it will make it ` . ` (thus making a split)

If you want to make sure something including a dot stays, you can use for example:

    t.keep("cool.")

### Contributing

It would be greatly appreciated if you want to contribute to this library.

It would also be great to add [contractions](https://github.com/kootenpv/contractions) for other languages.
