
from . import parser

class CalcParser(parser.Parser):
    def start(self):
        return self.expression()

    def expression(self):
        rv = self.match('term')
        while True:
            op = self.maybe_keyword('+', '-')
            if op is None:
                break

            term = self.match('term')
            if op == '+':
                rv += term
            else:
                rv -= term

        return rv

    def term(self):
        rv = self.match('factor')
        while True:
            op = self.maybe_keyword('*', '/')
            if op is None:
                break

            term = self.match('factor')
            if op == '*':
                rv *= term
            else:
                rv /= term

        return rv

    def factor(self):
        if self.maybe_keyword('('):
            rv = self.match('expression')
            self.keyword(')')

            return rv

        return self.match('number')

    def number(self):
        chars = []

        sign = self.maybe_keyword('+', '-')
        if sign is not None:
            chars.append(sign)

        chars.append(self.char('0-9'))

        while True:
            char = self.maybe_char('0-9')
            if char is None:
                break

            chars.append(char)

        if self.maybe_char('.'):
            chars.append('.')
            chars.append(self.char('0-9'))

            while True:
                char = self.maybe_char('0-9')
                if char is None:
                    break

                chars.append(char)

        rv = float(''.join(chars))
        return rv
    
if __name__ == '__main__':
    parser = CalcParser()

    while True:
        try:
            print(parser.parse(input('> ')))
        except KeyboardInterrupt:
            print()
        except (EOFError, SystemExit):
            print()
            break
        except (parser.ParseError, ZeroDivisionError) as e:
            print('Error: %s' % e)