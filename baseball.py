#-*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging

import random
import json
from game import Game

class Baseball(Game):
    GAME_NAME = 'Baseball'
    MAX_NUMBER_LENGTH = 32
    DEFAULT_NUMBER_LENGTH = 3
    DEFAULT_GAME_COUNT = 10

    def __init__(self, number, length=DEFAULT_NUMBER_LENGTH, count=DEFAULT_GAME_COUNT,
                 name=GAME_NAME, running=True, exclude=[]):
        super(self.__class__, self).__init__(name, running)
        self.length = length
        self.count = count
        self.number = number
        self.exclude = exclude

    @staticmethod
    def load_from_json(json_data):
        try:
            j = json.loads(json_data)
            return Baseball(**j)
        except:
            return None

    def info(self):
        info = """%d 자리 숫자 야구 게임을 시작합니다.
수의 범위는 1부터 9입니다. %d번 도전 할 수 있습니다.""" % (self.length, self.count)
        return info

    def __str__(self):
        try:
            super(self.__class__, self).__str__()
            return json.dumps(self.__dict__, indent=4)
        except:
            return ""

    def get_count(self):
        return self.count

    def run_game(self, user):
        value = self._validate(user)
        if value:
            return value

        result = self._judge_strike(user) | self._judge_ball(user)
        s = self._get_strike(result)
        b = self._get_ball(result)

        if result == 0:
            self._add_exclude(user)

        if s == self.length:
            self.end_game()
            return "당신이 이겼습니다!"

        self._decrease()

        if self.count <= 0:
            self.end_game()
            return "%dStrike(s) and %dBall(s). /baseball 로 재시작해주세요." % (s, b)

        return "%dStrike(s) and %dBall(s). %d회 남았습니다." % (s, b, self.count)

    def _add_exclude(self, value):
        exclude_value = str(self.exclude)
        for char in value:
            if char not in exclude_value:
                self.exclude += char

    @staticmethod
    def make_game(num_length=DEFAULT_NUMBER_LENGTH):
        if num_length >= Baseball.MAX_NUMBER_LENGTH:
            return None

        game = ""
        while len(game) != num_length:
            value = random.randrange(1, 10)
            str_value = ("%d" % value)
            if game.find(str_value) >= 0:
                continue
            game += str_value
        print game
        return game

    def _validate(self, user):
        if not self.running:
            return "Game has already stopped."

        if self.count <= 0:
            return "Sorry. Please restart again."

        if (not user.isdigit()) | (not len(user) == self.length):
            return "Please input %d length digit number." % self.length 

        has_zero = False
        char_value = {}
        for i in range(0, len(user)):
            if user[i] == '0':
                has_zero = True
            key = user[i]
            char_value[key] = key

        if has_zero:
            return "Please input 1 ~ 9 number."

        if not len(char_value) == self.length:
            return "Please input different number."
        return None

    def _decrease(self):
        if self.count > 0:
            self.count -= 1
        else:
            self.running = False
        return self.count

    def _get_strike(self, result):
        c = 0
        for index in range(0, self.length):
            if result & (1 << index):
                c += 1
        return c

    def _get_ball(self, result):
        c = 0
        for index in range(0, self.length):
            if result & (1 << (index + self.length)):
                c += 1
        return c
    
    def _contain(self, strValue, charValue, index):
        i = strValue.find(charValue)
        return (i >= 0) & (i != index)

    def _judge_strike(self, value):
        result = 0
        for index in range(0, len(self.number)):
            if self.number[index] == value[index]:
                result += (1 << (index))
        return result

    def _judge_ball(self, value):
        result = 0
        for index in range(0, len(self.number)):
            if self._contain(self.number, value[index], index):
                result += (1 << (index + self.length))
        return result
    
def Main():
    print "Baseball Game!"

    value = Baseball.make_game()

    bb = Baseball(value)

    while True:
        left = bb.count
        if left <= 0:
            n = bb.number
            print "Game Over! %s" % str(n)
            exit()

        print "Left count = ", left
        val = input("Guess ? ")

        result = bb.run_game(str(val));

        print result
        print bb.exclude

        if not bb.running:
            print "Game Over!"
            return

if __name__ == '__main__':
    Main()
