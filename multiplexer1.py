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

import collections
import random

random.seed(917)  # Not truly random for ease of regression testing


def main():
    totalCounter = Counter()
    carCounter = Counter("cars")
    commercialCounter = Counter("vans", "trucks")

    multiplexer = Multiplexer()
    for eventName, callback in (("cars", carCounter),  # the instance of Counter() is callable for its __call__
            ("vans", commercialCounter), ("trucks", commercialCounter)):
        multiplexer.connect(eventName, callback)
        multiplexer.connect(eventName, totalCounter)  # add each event into total #

    for event in generate_random_events(100):  # event is class not a instance
        multiplexer.send(event)
    print("After 100 active events:  cars={} vans={} trucks={} total={}"
            .format(carCounter.cars, commercialCounter.vans,
                    commercialCounter.trucks, totalCounter.count))

    multiplexer.state = Multiplexer.DORMANT
    for event in generate_random_events(100):
        multiplexer.send(event)
    print("After 100 dormant events: cars={} vans={} trucks={} total={}"
            .format(carCounter.cars, commercialCounter.vans,
                    commercialCounter.trucks, totalCounter.count))
    print('Nothing changed in DORMANT mode')
    
    multiplexer.state = Multiplexer.ACTIVE
    for event in generate_random_events(100):
        multiplexer.send(event)
    print("After 100 active events:  cars={} vans={} trucks={} total={}"
            .format(carCounter.cars, commercialCounter.vans,
                    commercialCounter.trucks, totalCounter.count))
    

def generate_random_events(count):  # random class generator
    vehicles = (("cars",) * 11) + (("vans",) * 3) + ("trucks",)  # set()
    for _ in range(count):
        yield Event(random.choice(vehicles), random.randint(1, 3))  # randint(a, b) return a int n: a<n<b


class Counter:
    # __init__(self, str)   __call__(self, instance of Event())
    def __init__(self, *names):
        self.anonymous = not bool(names)
        if self.anonymous:
            self.count = 0  # totalCounter.count = 0
        else:
            for name in names:  # name: cars, vans, trucks
                if not name.isidentifier():  # Return True if the string is a valid Python identifier, False otherwise.
                                             # class, def is not a identifier.
                    raise ValueError("names must be valid identifiers")
                setattr(self, name, 0)  # init: commercialCounter.vans = 0

    def __call__(self, event):  # make carCounter(event) callable, event here is class Event() not a instance
        if self.anonymous:  # if no name input, anonymous = 1
            self.count += event.count
        else:
            count = getattr(self, event.name)
            setattr(self, event.name, count + event.count)


class Event:

    def __init__(self, name, count=1):
        if not name.isidentifier():
            raise ValueError("names must be valid identifiers")
        self.name = name
        self.count = count


class Multiplexer:  # observer mode

    ACTIVE, DORMANT = ("ACTIVE", "DORMANT")  # flag: do nothing when Multiplexer.DORMANT

    def __init__(self):
        self.callbacksForEvent = collections.defaultdict(list)  # self.callbacksForEvent = {key:list[count1, count2...]}
        self.state = Multiplexer.ACTIVE

    def connect(self, eventName, callback):  # register
        if self.state == Multiplexer.ACTIVE:
            self.callbacksForEvent[eventName].append(callback)

    def disconnect(self, eventName, callback=None):  # un-register
        if self.state == Multiplexer.ACTIVE:
            if callback is None:
                del self.callbacksForEvent[eventName]  # del the key in dict: del all related callable
            else:
                self.callbacksForEvent[eventName].remove(callback)  # del the callable from the list related to the key

    def send(self, event):  # notify
        if self.state == Multiplexer.ACTIVE:
            for callback in self.callbacksForEvent.get(event.name, ()):  # dict.get(key, default=None)
                # event.name, that is eventName in def connect
                # print(event.name)
                callback(event)  # __call__(self, instance of Event())
                # callback loops in [carCounter, totalCounter] or [commercialCounter, totalCounter]


if __name__ == "__main__":
    main()
