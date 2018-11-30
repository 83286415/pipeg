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

import datetime
import itertools
import sys
import time


def main():
    historyView = HistoryView()
    liveView = LiveView()
    model = SliderModel(0, 0, 40)  # minimum, value, maximum
    model.observers_add(historyView, liveView)  # liveView produces output
    for value in (7, 23, 37):
        model.value = value                     # liveView produces output
    for value, timestamp in historyView.data:
        print(value, timestamp)
        print("{:3} {}".format(value, datetime.datetime.fromtimestamp(
                timestamp)), file=sys.stderr)


class Observed:

    def __init__(self):
        self.__observers = set()

    def observers_add(self, observer, *observers):  # more than one observer input  (book P98☆)
        for observer in itertools.chain((observer,), observers):  # loop in more than one observers
            # this for == for observer in (observer, ) + observers
            self.__observers.add(observer)
            observer.update(self)  # when added, update it right now

    def observer_discard(self, observer):
        self.__observers.discard(observer)  # discard: remove it from set()

    def observers_notify(self):
        for observer in self.__observers:
            observer.update(self)  # update() is to coded in observers for they are different


class SliderModel(Observed):

    def __init__(self, minimum, value, maximum):
        super().__init__()
        # These must exist before using their property setters
        self.__minimum = self.__value = self.__maximum = None
        self.minimum = minimum
        self.value = value
        self.maximum = maximum

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if self.__value != value:
            self.__value = value
            self.observers_notify()  # when setting this value, update observer's tim stamp

    @property
    def minimum(self):
        return self.__minimum

    @minimum.setter
    def minimum(self, value):
        if self.__minimum != value:
            self.__minimum = value
            self.observers_notify()  # when setting this value, update observer's tim stamp

    @property
    def maximum(self):
        return self.__maximum

    @maximum.setter
    def maximum(self, value):
        if self.__maximum != value:
            self.__maximum = value
            self.observers_notify()  # when setting this value, update observer's tim stamp


class HistoryView:

    def __init__(self):
        self.data = []

    def update(self, model):
        self.data.append((model.value, time.time()))  # the time stamp of which this line runs


class LiveView:

    def __init__(self, length=40):
        self.length = length

    def update(self, model):
        tippingPoint = round(model.value * self.length /
                (model.maximum - model.minimum))  # keep tippingPoint a int not a float
        td = '<td style="background-color: {}">&nbsp;</td>'
        html = ['<table style="font-family: monospace" border="0"><tr>']
        html.extend(td.format("darkblue") * tippingPoint)  # extend: add another list to this one's tail
        html.extend(td.format("cyan") * (self.length - tippingPoint))
        html.append("<td>{}</td></tr></table>".format(model.value))  # the number at the end of the line filled with box
        print("".join(html))


if __name__ == "__main__":
    main()
