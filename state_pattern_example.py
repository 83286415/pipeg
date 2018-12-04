#!/usr/bin/env python
# -*- coding:utf-8 -*-


class State(object):  # Abstract State  class
    def __init__(self):
        pass

    def write_program(self, w):
        pass


class Work(object):  # Context class
    def __init__(self):
        self.hour = 9
        self.curr = ForenoonState()

    def set_state(self, s):
        self.curr = s

    def write_program(self):
        self.curr.write_program(self)


class ForenoonState(State):  # Concrete State class

    def write_program(self, w):
        if w.hour < 12:
            print("当前时间:%s点," % w.hour, "精神百倍")
        else:
            w.set_state(AfternoonState())
            w.write_program()


class AfternoonState(State):  # Concrete State class

    def write_program(self, w):
        if w.hour < 17:
            print("当前时间:%s点," % w.hour, "状态还行,继续努力")
        else:
            w.set_state(EveningState())
            w.write_program()


class EveningState(State):  # Concrete State class

    def write_program(self, w):
        if w.hour < 21:
            print("当前时间:%s点," % w.hour, "加班呢,疲劳了")
        else:
            w.set_state(SleepState())
            w.write_program()


class SleepState(State):  # Concrete State class

    def write_program(self, w):
        print("当前时间:%s点," % w.hour, "不行了,睡着了")


if __name__ == "__main__":
    work = Work()
    work.hour = 9
    work.write_program()
    work.hour = 15
    work.write_program()
    work.hour = 20
    work.write_program()
    work.hour = 22
    work.write_program()
