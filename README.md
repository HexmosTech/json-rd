# json-rd

This project hosts a recursive descent parser for JSON in pure python. 
I started the project following a tutorial on the topic, [Building Recursive
Descent Parsers: The Definitive Guide](https://www.booleanworld.com/building-recursive-descent-parsers-definitive-guide/). Once through the
tutorial, I applied tests from the [JSONTestSuite](https://github.com/nst/JSONTestSuite)
to the resultant code. I noticed quite a few tests cases failing, especially
related to escaping, numbers and special characters. So, I set out to build a 
more compliant & also *flexible* JSON parser in pure python.

`json-rd` is different from the standard JSON in a few ways:

1. Allows comments starting with `#`
1. Allows single quoted strings
1. Is less strict about number formatting in some cases (ex: `1 000`, `- 1` are considered valid & parsed successfully)
1. Ignores trailing garbage to a legal JSON structure

## Tutorials

To learn more about recursive descent parsing, I highly recommend working through
[Building Recursive Descent Parsers: The Definitive Guide](https://www.booleanworld.com/building-recursive-descent-parsers-definitive-guide/). The file [parser.py](./src/parser.py)
is from this original tutorial. Thanks to the author in sharing such a great resource
with the world.


## How-to

### How do I run the test cases?

Run:

```
python -m src.test_jsonparser
```

### How do I remove single quote support?

In [jsonparser](./src/jsonparser.py), goto the `quoted_string` method.

Find the line:

```
quote = self.char("\"'")
```

Replace with:
```
quote = self.char('"')
```

### How do I debug my parser?

This is my VSCode debug configuration:

```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Module",
            "type": "python",
            "request": "launch",
            "module": "src.test_jsonparser",
            "justMyCode": true
        }
    ]
}
```

To debug particular case, one can add a *conditional breakpoint* such as:

```
"partial_filename" in m
```

Where `m` is one of the loop variables iterating through various sample JSON
files.

## Explanation

How does a recursive parser work in a nutshell? What's a nice way
to think about them, as a programmer/engineer?

First of all it is important to understand some of the primitives in
[parser.py](./src/parser.py). The most basic ones are the following:

- `char`: Expect next character to be X. We can express X as a character class (ex: `0-9`).
If expectation not met, throw `ParseError`
- `keyword`: Expect a sequence of characters XYZ. On failure to find the sequence, throw `ParseError`


The next most important primitive is:

- `match`: Take a list of rules (essentially python functions) and apply them
in order. Return on first successful match; on failure throw `ParseError`. Each of
the `match` rules tend to be implemented through `char`, `keyword` and basic python
such as conditionals/loops.

These are the only primitives required to build a recursive descent parser!

For example, an EBNF `a :== b | c | d` can be defined as 4 python functions `a`,
`b`, `c`, `d`; one can simply do `match(b, c, d)` to apply the rules in the 
requisite order.

Moreover, the library offers some nice convenience functions built on top of the
primitives mentioned above:

- `maybe_char`: Try matching a char; on failure return `None`
- `maybe_keyword`: Try matching a keyword; on failure return `None`
- `maybe_match`: Try matching a given rule/function; on failure, return `None`

These help with avoiding `try/catch` structure on failing to match some piece
of text.

## Reference

1. [Building Recursive Descent Parsers: The Definitive Guide - Boolean World](https://www.booleanworld.com/building-recursive-descent-parsers-definitive-guide/): Tutorial on recursive
descent parsers
1. [JSON.org](https://www.json.org/json-en.html): Nice rail road diagram of the grammar
1. [JSON McKeeman Form](https://www.crockford.com/mckeeman.html): Simple grammar specification
in EBNF-type format
1. [Railroad Diagram Generator](https://www.bottlecaps.de/rr/ui): Generate railroad diagrams for 
visualizing grammar