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


def main():
    form = Form()
    test_user_interaction_with(form)


class Form:

    def __init__(self):
        self.create_widgets()
        self.create_mediator()

    def create_widgets(self):
        self.nameText = Text()
        self.emailText = Text()
        self.okButton = Button("OK")
        self.cancelButton = Button("Cancel")

    def create_mediator(self):  # register widgets and their update methods in pairs
        self.mediator = Mediator(((self.nameText, self.update_ui),  # pairs: (widget instance, callable)
                (self.emailText, self.update_ui),
                (self.okButton, self.clicked),
                (self.cancelButton, self.clicked)))
        self.update_ui()  # when init create mediator, this make button.enable False

    def update_ui(self, widget=None):  # update the button ui: allow it to click only if name and email are both input
        self.okButton.enabled = (bool(self.nameText.text) and
                                 bool(self.emailText.text))

    def clicked(self, widget):  # widget is the buttons, name text, email text widgets instance
        if widget == self.okButton:
            print("OK")  # not only prints ok, it should do something more, like send data to data base
        elif widget == self.cancelButton:
            print("Cancel")


class Mediator:

    def __init__(self, widgetCallablePairs):
        self.callablesForWidget = collections.defaultdict(list)  # dict callableForWidget's value type is list
        for widget, caller in widgetCallablePairs:
            self.callablesForWidget[widget].append(caller)
            widget.mediator = self  # make itself a widget's attribute
        # print(self.callablesForWidget)

    def on_change(self, widget):  # is to change the status of widgets
        callables = self.callablesForWidget.get(widget)
        if callables is not None:
            for caller in callables:  # caller: update_ui, clicked
                caller(widget)
        else:
            raise AttributeError("No on_change() method registered for {}"
                    .format(widget))


class Mediated:  # meta class of button and text class
    # To make it into a candy, refer to mediator1d.py
    def __init__(self):
        self.mediator = None

    def on_change(self):
        if self.mediator is not None:
            self.mediator.on_change(self)  # self here is the widget in Mediator.on_charge(self, widget)


class Button(Mediated):

    def __init__(self, text=""):
        super().__init__()
        self.enabled = True
        self.text = text

    def click(self):
        if self.enabled:  # enable or disable depends on texts input or not
            self.on_change()

    def __str__(self):  # for printing Button()
        return "Button({!r}) {}".format(self.text,
                "enabled" if self.enabled else "disabled")


class Text(Mediated):

    def __init__(self, text=""):
        super().__init__()
        self.__text = text

    @property
    def text(self):
        return self.__text

    @text.setter  # make the property text importable
    def text(self, text):
        if self.text != text:
            self.__text = text
            self.on_change()

    def __str__(self):
        return "Text({!r})".format(self.text)


def test_user_interaction_with(form):
    form.okButton.click()           # Ignored because it is disabled
    print(form.okButton.enabled)    # False: the color of the button is grey
    form.nameText.text = "Fred"
    print(form.okButton.enabled)    # False
    form.emailText.text = "fred@bloggers.com"
    print(form.okButton.enabled)    # True
    form.okButton.click()           # OK: e.g. send name and email info to database
    form.emailText.text = ""
    print(form.okButton.enabled)    # False
    form.cancelButton.click()       # Cancel: e.g. get back to last page


if __name__ == "__main__":
    main()

