__project__ = "tokenize"
__version__ = "0.0.5"
__repo__ = "https://github.com/kootenpv/tok"

import string
from textsearch import TextSearch
from contractions import contractions_dict, leftovers_dict

ABBREVS = (
    "a.m.",
    "Adm.",
    "Bros.",
    "co.",
    "Corp.",
    "D.C.",
    "Dr.",
    "e.g.",
    "Gen.",
    "Gov.",
    "i.e.",
    "Inc.",
    "Jr.",
    "Ltd.",
    "Md.",
    "Messrs.",
    "Mo.",
    "Mont.",
    "Mr.",
    "Mrs.",
    "Ms.",
    "p.m.",
    "Ph.D.",
    "Rep.",
    "Rev.",
    "Sen.",
    "St.",
    "vs.",
)


class Tokenizer:
    def __init__(
        self,
        handle_http=False,
        handle_domains=False,
        numbers=True,
        combine_punctuation=True,
        eol="\n",
        currencies=("$",),
        protected_words=None,
        contractions=True,
        language="en",
        abbrevs=ABBREVS,
    ):
        # set() set() should fallback to just using __iter__ of automaton for a speedboost
        if language != "en" and contractions:
            raise ValueError("No contractions known for languages other than English.")
        self.contractions = contractions
        self.tokenizer = None
        self.handle_http = handle_http
        self.handle_domains = handle_domains
        self.combine_punctuation = combine_punctuation
        self.numbers = numbers
        self.eol = eol
        self.currencies = currencies or []
        self.protected_words = protected_words or []
        self.abbrevs = abbrevs
        self.explain_dict = {}
        self.setup()

    def setup(self):
        self.tokenizer = TextSearch("sensitive", "norm", set(), set())
        self.add_base_cases()
        self.add_currencies()
        self.add_words(self.protected_words)
        if self.handle_http:
            self.tokenizer.add_http_handler(keep_result=True)
            for word in ["http://", "https://", "www."]:
                self.explain_dict[
                    word
                ] = "regex: when it finds '{}' it will stop after it finds a space.".format(word)
        if self.handle_domains:
            self.add_domain_handler()
        if self.contractions:
            if self.contractions == True:
                self.contractions = {}
                self.contractions.update(contractions_dict)
                self.contractions.update(leftovers_dict)
            self.add_words(self.contractions)
        if self.abbrevs:
            self.add_words(self.abbrevs)

    def add_words(self, words):
        # [("cannot", "can not"), ("can't", "can n't"), ("mr.", "mr.")]
        words = words.items() if isinstance(words, dict) else words
        if words and isinstance(words, (list, set, tuple)) and isinstance(words[0], str):
            words = [(x, x) for x in words]
        for x, y in words:
            REASON_AS_IS = "protected word: adds word as is, prevents splitting it."
            REASON_UPPER = "protected word: adds word uppercased, prevents splitting it."
            REASON_TITLE = "protected word: adds word titlecased, prevents splitting it."
            self.add(x, y, REASON_AS_IS)
            self.add(x.upper(), y.upper(), REASON_UPPER)
            self.add(x[0].upper() + x[1:], y[0].upper() + y[1:], REASON_TITLE)

    def add_domain_handler(self):
        import re
        from tldextract.tldextract import TLD_EXTRACTOR

        valid_re = re.compile("^[a-zA-Z.]+$")
        tlds = ["." + x for x in TLD_EXTRACTOR.tlds if valid_re.match(x)]

        for x in tlds:
            self.add(x, x, "Added by domain handler, keeps the token existing.")

    def add_base_cases(self):
        if self.numbers:
            for x in "0123456789":
                self.keep(x + ",")
                self.keep(x + ".")

        # self.tokenizer.add(" !", " ! ")

        if self.combine_punctuation:
            # combine multiples
            R_COMBINE = "combine punctuation: merges '{}' into '{}' and starts a new sentence."
            for s in "!.?-":
                for i in range(2, 10):
                    # one of these is a splitting char
                    if i == 1 and s == "-":
                        continue
                    c = s * i
                    e = s * 3 if i > 1 else s
                    # end = "$<EOS>$" if i == 1 or s != "-" else " "
                    end = " \n" if i == 1 or s != "-" else " "
                    self.add(c, " {}{}".format(e, end), R_COMBINE.format(c, e + end))

            for i in range(2, 10):
                # self.tokenizer.add("\n" * i, "$<EOS>$")
                self.add("\n" * i, " \n ", "merges newlines")

        for s in "!.?-\n":
            self.split(s, "Splits on '{}' and creating a new sentence.".format(s))

        self.split("- ")

        self.split("...")

        # does not work
        # self.tokenizer.add_regex_handler(["!?"], "[!]+[?]+[!?]+", True, return_value=" !? ")

        self.split("!?")
        self.split("!?!")
        self.split("!!?")
        self.split("!??")
        self.split("?!!")
        self.split("?!?")
        self.split("??!")

        for x in string.ascii_letters:
            self.keep(" " + x + ".")

        # for x in string.ascii_letters:
        #     self.tokenizer.add("\n" + x, "\n" + x)

        self.split(",")

        # quotes (make sure we add all the exeptions)
        self.split("'")
        self.split('"')

    def keep(self, x, reason=None):
        """ Whenever it finds x, it will not add whitespace. Prevents direct tokenization. """
        self.tokenizer.add(x, x)
        self.explain_dict[x] = reason or "keep:" + self.keep.__doc__.replace("x", repr(x)).rstrip()

    def split(self, x, reason=None):
        """ Whenever it finds x, it will surround it by whitespace, thus creating a token. """
        self.tokenizer.add(x, " {} ".format(x))
        self.explain_dict[x] = (
            reason or "split:" + self.split.__doc__.replace("x", repr(x)).rstrip()
        )

    def drop(self, x, reason=None):
        """ Whenever it finds x, it will remove it but add a split."""
        self.tokenizer.add(x, " ")
        self.explain_dict[x] = reason or "drop:" + self.drop.__doc__.replace("x", repr(x)).rstrip()

    def strip(self, x, reason=None):
        """ Whenever it finds x, it will remove it without splitting. """
        self.tokenizer.add(x, "")
        self.explain_dict[x] = (
            reason or "strip:" + self.strip.__doc__.replace("x", repr(x)).rstrip()
        )

    def add(self, x, y, reason):
        self.tokenizer.add(x, y)
        self.explain_dict[x] = reason

    def explain(self, char_or_chars):
        keys = [x for x in self.tokenizer._root_dict if char_or_chars in x]
        if not keys:
            return {
                "explanation": "No explanation, meaning there is nothing specified for the input"
            }
        return [
            {"from": x, "to": self.tokenizer._root_dict[x], "explanation": self.explain_dict[x]}
            for x in keys
        ]

    def remove(self, x, reason=None):
        self.tokenizer.remove(x)
        self.explain_dict[x] = reason or "removing '{}'".format(x)

    def add_currencies(self):
        for currency in self.currencies:
            self.split(currency)

        for num in "0123456789":
            # to prevent the . and , from being treated as punct
            for punc in ",.":
                s = "{currency}{num}{punc}".format(currency=currency, num=num, punc=punc)
                r = " {currency} {num}{punc}".format(currency=currency, num=num, punc=punc)
                self.add(s, r, "protecting currency from being seen as a number.")

    def word_tokenize(self, z, return_entities=False, to_lower=False):
        if return_entities:
            a, b = self.tokenizer.replace(" " + z, return_entities=True)
            return a.split(), b
        res = self.tokenizer.replace(" " + z).split()
        if to_lower:
            res = [x.lower() for x in res]
        return res

    def word_newlined_tokenize(self, z):
        sentences = self.sent_tokenize(z)
        return sum([x + ["\n"] for x in sentences[:-1]], []) + sentences[-1]

    def sent_tokenize(self, z):
        return [x.split() for x in self.tokenizer.replace(z).split("\n") if x.strip()]


t = Tokenizer(handle_http=True, handle_domains=False)
word_tokenize = t.word_tokenize
sent_tokenize = t.sent_tokenize
