# -*- coding: utf-8 -*-
# !/usr/bin/env python
import sys
import logging
import json
from random import *
from game import Game

reload(sys)
sys.setdefaultencoding('utf-8')

class Arithmetic(Game):
    ID = '/arithmetic'
    NAME = 'Arithmetic'
    CLASS_NAME = 'arithmetic.Arithmetic'
    INFO = (ID, CLASS_NAME)
    DEFAULT_START_NUMBER = 1
    DEFAULT_END_NUMBER = 100

    MSGS_CNT = 5
    SUCCESS_MSGS = ['와우!', '훌륭해요!', '장난아닌데!', '그레이트!', '맞았습니다!']
    FAIL_MSGS = ['저런', '아우', '아깝습니다.', '잘해봐요.', '틀렸습니다.']
    OPERATORS = ['+', '-', '*']

    def __init__(self, x=-1, y=-1, op=OPERATORS[0], start=DEFAULT_START_NUMBER, end=DEFAULT_END_NUMBER,
                 name=NAME, win=0, lose=0, running=True):
        super(self.__class__, self).__init__(name, running)
        self.start = start
        self.end = end
        self.win = win
        self.lose = lose
        self.x = x
        self.y = y
        self.op = op
        if self.x == -1:
            self.x = randint(self.start, self.end)
        if self.y == -1:
            self.y = randint(self.start, self.end)

    def load(self, json_data):
        try:
            j = json.loads(json_data)
            return Arithmetic(**j)
        except Exception as e:
            logging.info(e)
            return None

    def __str__(self):
        try:
            super(self.__class__, self).__str__()
            return json.dumps(self.__dict__, indent=4)
        except Exception as e:
            logging.info(e)
            return ""

    def _question(self):
        return "%d %s %d 은 얼마인가요 ? " % (self.x, self.op, self.y)

    def start_game(self):
        super(self.__class__, self).start_game()
        msg = "숫자 맞추기 게임입니다.\n"
        msg += self._question()
        return msg

    def result(self):
        if self.op == '+':
            return self.x + self.y
        if self.op == '-':
            return self.x - self.y
        if self.op == '*':
            return self.x * self.y
        return 0

    @staticmethod
    def swap(x, y):
        return y, x

    def run_game(self, user_input):
        value = self._validate(user_input)
        if value:
            return value

        msg = None
        if int(user_input) == self.result():
            self.win += 1
            msg = self.SUCCESS_MSGS[randint(0, 5)]
        else:
            self.lose += 1
            msg = self.FAIL_MSGS[randint(0, 5)]
            msg += " 정답은 %d 입니다." % self.result()

        msg += "\n"
        msg += "전적은 %d승 %d패 입니다.\n" % (self.win, self.lose)

        self.op = self.OPERATORS[randint(0, len(self.OPERATORS))]

        self.x = randint(self.start, self.end)
        self.y = randint(self.start, self.end)

        if self.op == '-' and self.x < self.y:
            self.swap(self.x, self.y)

        if self.op == '*':
            self.y = randint(1, 9)

        msg += self._question()

        return msg

    def _validate(self, user):
        if not self.running:
            return "게임이 이미 종료되었습니다."
        if not user.isdigit():
            return "숫자로 입력해 주세요."

        return None


def Main():
    print "Arithmetic game"

    aa = Arithmetic()
    msg = aa.start_game()
    print msg

    while True:
        val = input("Guess ? ")
        result = aa.run_game(str(val));
        print result


if __name__ == '__main__':
    Main()
