#!/usr/bin/env python

class Game(object):

    def __init__(self, name, running):
        self.name = name
        self.running = running

    @staticmethod
    def load_from_json(json_data):
        return

    def get_name(self):
        return self.name

    def validate(self):
        return None

    def run_game(self, value):
        return None

    def end_game(self):
        self.running = False

    def info(self):
        return None

    def help(self):
        return None

    def __str__(self):
        return "This is a %s game" % self.name
