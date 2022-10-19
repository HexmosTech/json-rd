#!/usr/bin/env python3

from audioop import mul
from .parser import *
import json
import unicodedata
import math


class JSONParser(Parser):
    """
    Start ::= AnyType
    AnyType ::= ComplexType | PrimitiveType
    ComplexType ::= List | Map
    List ::= "[" (AnyType ",")* AnyType? "]"
    Map ::= "{" (Pair ",")* Pair? "}"
    Pair ::= (QuotedString | UnquotedString) ":" AnyType
    PrimitiveType ::= Null | Boolean | QuotedString | Number
    Number ::= Integer | Fraction | Exponent
    Integer ::= Digit | Onenine Digits | '-' Digit | '-' Onenine Digits
    Digits ::= Digit | Digit Digits
    Digit ::= '0' | Onenine
    OneNine ::= [1-9]
    Fraction ::= '.' Digits | ""
    Exponent ::= 'E' Sign Digits | 'e' Sign Digits | ""
    Sign ::= '+' | '-' | ""
    """

    def eat_whitespace(self):
        is_processing_comment = False

        while self.pos < self.len:
            char = self.text[self.pos + 1]
            if is_processing_comment:
                if char == "\n":
                    is_processing_comment = False
            else:
                if char == "#":
                    is_processing_comment = True
                elif char not in " \f\v\r\t\n":
                    break

            self.pos += 1

    def start(self):
        return self.match("any_type")

    def any_type(self):
        return self.match("complex_type", "primitive_type")

    def primitive_type(self):
        return self.match("null", "boolean", "quoted_string", "number")

    def complex_type(self):
        return self.match("list", "map")

    def list(self):
        rv = []

        self.keyword("[")
        comma = False
        while True:
            item = self.maybe_match("any_type")
            try:
                # print("item = ", item.encode('utf-8', 'replace').decode())
                pass
            except:
                # print(item)
                pass
            if item is None:
                break

            rv.append(item)

            if not self.maybe_keyword(","):
                comma = False
                break
            else:
                comma = True

        self.keyword("]")
        if comma == True:
            raise ParseError(
                self.pos, "Unnecessary trailing comma found", self.text[self.pos]
            )
        return rv

    def map(self):
        rv = {}

        self.keyword("{")
        comma = False
        while True:
            item = self.maybe_match("pair")
            if item is None:
                break

            rv[item[0]] = item[1]

            if not self.maybe_keyword(","):
                comma = False
                break
            else:
                comma = True

        self.keyword("}")
        if comma == True:
            raise ParseError(
                self.pos, "Unnecessary trailing comma found", self.text[self.pos]
            )

        return rv

    def pair(self):
        key = self.match("quoted_string")

        if type(key) is not str:
            raise ParseError(
                self.pos + 1, "Expected string but got number", self.text[self.pos + 1]
            )

        self.keyword(":")
        value = self.match("any_type")

        return key, value

    def null(self):
        self.keyword("null")
        return "null"

    def boolean(self):
        boolean = self.keyword("true", "false")
        return boolean[0] == "t"

    def number(self):
        intpart = self.match("integer")
        fracpart = self.match("fraction")
        expart = self.match("exponent")
        if expart != 0:
            return (intpart + fracpart) * math.pow(10, expart)
        else:
            return intpart + fracpart

    def integer(self):
        return int(
            self.match(
                "integer_rule_4", "integer_rule_3", "integer_rule_2", "integer_rule_1"
            )
        )

    def integer_rule_1(self):
        return self.match("digit")

    def integer_rule_2(self):
        s = []
        ionenine = self.match("onenine")
        if ionenine is not None:
            s.append(ionenine)

        idigits = self.match("digits")
        if idigits is not None:
            s.append(idigits)

        return "".join(s)

    def integer_rule_3(self):
        s = []
        nsign = self.char("-")
        if nsign is not None:
            s.append(nsign)
        r = self.match("integer_rule_1")
        s.append(r)
        return "".join(s)

    def integer_rule_4(self):
        s = []
        nsign = self.char("-")
        if nsign is not None:
            s.append(nsign)
        r = self.match("integer_rule_2")
        s.append(r)
        return "".join(s)

    def fraction(self):
        try:
            return float(self.match("fraction_rule_1"))
        except ParseError:
            return 0

    def fraction_rule_1(self):
        s = []
        s.append(self.char("."))
        s.append(self.match("digits"))
        return "".join(s)

    def exponent(self):
        try:
            return self.match("exponent_rule_1")
        except ParseError:
            return 0

    def exponent_rule_1(self):
        self.char("eE")
        esign = self.match("sign")
        multiplier = None
        if esign == "+" or esign == "":
            multiplier = 1
        else:
            multiplier = -1
        return multiplier * int(self.match("digits"))

    def digits(self):
        s = []
        r = self.match("digit")
        s.append(r)
        while True:
            r = self.maybe_match("digit")
            if r is None:
                break
            s.append(r)
        return "".join(s)

    def digit(self):
        s = self.maybe_char("0")
        if not s is None:
            return s

        return self.match("onenine")

    def onenine(self):
        s = self.char("1-9")
        return s

    def sign(self):
        s = self.maybe_char("+-")
        if s is None:
            return ""
        else:
            return s

    def quoted_string(self):
        quote = self.char("\"'")
        chars = []

        escape_sequences = {
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
            "\\": "\\",
            "/": "/",
            quote: f"\{quote}",
        }

        while True:
            char = self.char()
            if char == quote:
                break
            elif char == "\\":
                escape = self.char()
                if escape == "u":
                    code_point = []
                    for i in range(4):
                        code_point.append(self.char("0-9a-fA-F"))

                    chars.append(chr(int("".join(code_point), 16)))
                else:
                    try:
                        chars.append(escape_sequences[escape])
                    except:
                        raise ParseError(
                            self.pos + 1,
                            "Invalid escape sequence",
                            self.text[self.pos + 1],
                        )

            else:
                if unicodedata.category(char) == "Cc":
                    raise ParseError(
                        self.pos + 1,
                        "Unescaped control character",
                        self.text[self.pos + 1],
                    )

                chars.append(char)

        try:
            res = "".join(chars)
        except Exception as e:
            raise e
        return res


if __name__ == "__main__":
    import sys
    from pprint import pprint

    parser = JSONParser()

    try:
        pprint(parser.parse(sys.stdin.read()))
    except ParseError as e:
        print("Error: " + str(e))
