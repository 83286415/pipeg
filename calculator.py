#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import collections
import math
import sys


if sys.version_info >= (3, 3):
    import types

    def main():
        quit = "Ctrl+Z,Enter" if sys.platform.startswith("win") else "Ctrl+D"
        prompt = "Enter an expression ({} to quit): ".format(quit)
        current = types.SimpleNamespace(letter="A")  # create a class with only one property "letter", its value is A
        globalContext = global_context()
        localContext = collections.OrderedDict()  # keep the order in which elements added into this dict
        while True:
            try:
                expression = input(prompt)
                if expression:
                    calculate(expression, globalContext, localContext, current)
            except EOFError:  # a file can be loaded
                print()
                break
else:
    def main():
        quit = "Ctrl+Z,Enter" if sys.platform.startswith("win") else "Ctrl+D"
        prompt = "Enter an expression ({} to quit): ".format(quit)
        current = type("_", (), dict(letter="A"))()  # create a class with only one property "letter", its value is A
        globalContext = global_context()
        localContext = collections.OrderedDict()
        while True:
            try:
                expression = input(prompt)
                if expression:
                    calculate(expression, globalContext, localContext, current)
            except EOFError:  # a file can be loaded
                print()
                break

# output:
# Enter an expression (Ctrl+Z,Enter to quit): 33
# A=33
# ANS=33
# Enter an expression (Ctrl+Z,Enter to quit): 22
# A=33, B=22
# ANS=22
# Enter an expression (Ctrl+Z,Enter to quit): 11
# A=33, B=22, C=11
# ANS=11
# Enter an expression (Ctrl+Z,Enter to quit): sin90
# name 'sin90' is not defined
# Enter an expression (Ctrl+Z,Enter to quit): sin(90)
# A=33, B=22, C=11, D=0.8939966636005579
# ANS=0.8939966636005579


def global_context():  # can be replaced by from math import *
    globalContext = globals().copy()
    # shallow copy: copy elements but quote sub-elements. So changed sub-elements can effect original one
    for name in dir(math):  # dir: a list of this module's attributes
        if not name.startswith("_"):
            globalContext[name] = getattr(math, name)
            # print(name, globalContext[name])  # Cython related. ignored.
    return globalContext


def calculate(expression, globalContext, localContext, current):
    try:
        result = eval(expression, globalContext, localContext)
        update(localContext, result, current)
        print(", ".join(["{}={}".format(variable, value)
                for variable, value in localContext.items()]))  # format + for
        print("ANS={}".format(result))
    except Exception as err:
        print(err)


def update(localContext, result, current):
    localContext[current.letter] = result  # localContext dict: {'A': result}
    current.letter = chr(ord(current.letter) + 1)  # refer to my cloud note, key word: ord
    if current.letter > "Z":  # only support 26 variables
        current.letter = "A"


if __name__ == "__main__":
    main()
