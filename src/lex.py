import enum
import sys

class Lexer:
    def __init__(self, source):
        self.source = source + '\n' # source code to lex as a string. append a newline to simplify lexing/parsing the last token/statement
        self.curChar = '' # current char in the string
        self.curPos = -1 # current position in the string
        self.nextChar()

    # process next character.
    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0' # EOF
        else:
            self.curChar = self.source[self.curPos]

    # return lookahead character.
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos+1]

    # invalid token found, print error and exit
    def abort(self, message):
        sys.exit("Lexing error. " + message)

    # skip whitespace except newline, used to indicate end of a statement
    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()

    # skip comments in the code
    def skipComment(self):
        if self.curChar == '#':
            while self.curChar != '\n':
                self.nextChar()

    # return next token
    def getToken(self):
        # if there is white space, skip it
        self.skipWhitespace()
        self.skipComment()
        token = None
        # check first character of token to see if we can decide what it is
        # If it is multi-char operator (!=, ...), number, identifier, or keyword then process rest
        if self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS)    # plus token
        elif self.curChar == '-':
            token = Token(self.curChar, TokenType.MINUS)    # minus token
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)    # asterisk token
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)    # slash token
        elif self.curChar == '=':
            # check whether token is = or ==
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ) # eqeq token
            else:
                token = Token(self.curChar, TokenType.EQ) # eq token
        elif self.curChar == '>':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.GTEQ) # greater than equal to token
            else:
                token = Token(self.curChar, TokenType.GT) # greater than token
        elif self.curChar == '<':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)
        elif self.curChar == '!':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, but only got !" + self.peek())
        elif self.curChar == '\"':
            # get characters between quotations
            self.nextChar()
            startPos = self.curPos

            while self.curChar != '\"':
                # dont allow special characters in string. no escape char, newlines, tabs, or %.
                # using C's printf on this string
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal character in string.")
                self.nextChar()

            tokText = self.source[startPos : self.curPos] # get the substring.
            token = Token(tokText, TokenType.STRING)

        # NUMBERS
        elif self.curChar.isdigit():
            # leading character is a digit, so it is a number
            # get all consecutive digits and decimal if there is one
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.': # decimal
                self.nextChar()

                if not self.peek().isdigit():
                    # error
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.curPos + 1] # get the substring
            token = Token(tokText, TokenType.NUMBER)
        elif self.curChar.isalpha():
            # Leading char is a letter, must be identifier or a keyword
            # get all consecutive alpha numeric characters
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()

            tokText = self.source[startPos : self.curPos + 1] # get the substring
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None: # identifier
                token = Token(tokText, TokenType.IDENT)
            else:
                token = Token(tokText, keyword)
        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.NEWLINE)    # newline token
        elif self.curChar == '\0':
            token = Token('', TokenType.EOF)    # EOF token
        else:
            # unknown token
            self.abort("Unknown token: " + self.curChar)

        self.nextChar()
        return token

class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText # tokens actual text. used for identifiers, strings, and numbers
        self.kind = tokenKind # the TokenType that this token is classified as

    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # relies on all keyword enum values being 1XX
            if kind.name == tokenText and kind.value >= 100 and kind.value <= 200:
                return kind
        return None

class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211