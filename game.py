#-*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Game(object):
    def __init__(self, name, running):
        self.name = name
        self.running = running

    def load(self, json_data):
        return

    def get_name(self):
        return self.name

    def run_game(self, value):
        return None

    def end_game(self):
        self.running = False

    def start_game(self):
        self.running = True
        return None

    def help(self):
        return "도움말 준비 중입니다."

    def keyboards(self):
        return None

    def __str__(self):
        return "This is a %s game" % self.name
