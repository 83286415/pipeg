#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import html.parser
import os
import re
import sys


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {"-h", "--help"}:
        print("usage: {} <files>".format(os.path.basename(sys.argv[0])))  # basename: returns the last name in path
        sys.exit(1)
    count_words_in_files(sys.argv[1:])


def count_words_in_files(files):
    total = 0
    for filename in files:
        count = count_words(filename)
        if count is not None:
            total += count
            print("{:9,} words in {}".format(count, filename))
    print("total: {:,} words".format(total))


def count_words(filename):
    for wordCounter in (PlainTextWordCounter, HtmlWordCounter):
        if wordCounter.can_count(filename):  # no instance for it's class method
            return wordCounter.count(filename)


class AbstractWordCounter:  # refer to wordcount2.py for metaclass=abc.ABCMeta

    @staticmethod
    def can_count(filename):
        raise NotImplementedError()  # used in abc better than pass

    @staticmethod
    def count(filename):
        raise NotImplementedError()


class PlainTextWordCounter(AbstractWordCounter):

    @staticmethod
    def can_count(filename):
        return filename.lower().endswith(".txt")  # return 1 if filename end with txt

    @staticmethod
    def count(filename):
        if not PlainTextWordCounter.can_count(filename):
            return 0  # it's not good to return 0 if filename does not end with txt!
        regex = re.compile(r"\w+")  # re \w+: at least one word, number or _; compile: return a re pattern
        total = 0
        with open(filename, encoding="utf-8") as file:
            for line in file:
                for _ in regex.finditer(line):  # finditer like findall but returns a iterator
                    total += 1
        return total


class HtmlWordCounter(AbstractWordCounter):

    class __HtmlParser(html.parser.HTMLParser):  # private parser only used in this class

        def __init__(self):
            super().__init__()
            self.regex = re.compile(r"\w+")
            self.inText = True
            self.text = []
            self.count = 0

        def handle_starttag(self, tag, attrs):
            if tag in {"script", "style"}:  # {} here used as () or []
                self.inText = False

        def handle_endtag(self, tag):  # count the words in this def
            if tag in {"script", "style"}:
                self.inText = True
            else:  # if the end tag is not script or style: count the words and then erase self.text list
                for _ in self.regex.finditer(" ".join(self.text)):
                    self.count += 1
                self.text = []

        def handle_data(self, text):  # put the words in self.text list
            if self.inText:
                text = text.rstrip()
                if text:
                    self.text.append(text)

    @staticmethod
    def can_count(filename):
        return filename.lower().endswith((".htm", ".html"))

    @staticmethod
    def count(filename):
        if not HtmlWordCounter.can_count(filename):
            return 0
        parser = HtmlWordCounter.__HtmlParser()  # make a parser instance
        with open(filename, encoding="utf-8") as file:
            parser.feed(file.read())  # https://www.cnblogs.com/zhanghaohong/p/4562127.html
        return parser.count


if __name__ == "__main__":
    main()
