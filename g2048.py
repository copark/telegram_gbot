# -*- coding: utf-8 -*-
# !/usr/bin/env python
import sys
import logging
import json
import random
from game import Game

reload(sys)
sys.setdefaultencoding('utf-8')


class Game2048(Game):
    ID = '/2048'
    NAME = '2048'
    CLASS_NAME = 'g2048.Game2048'
    INFO = (ID, CLASS_NAME)
    DEFAULT_LENGTH = 4

    keys = ['left', 'up', 'down', 'right']

    def __init__(self, length=DEFAULT_LENGTH, grid="", name=NAME, running=True):
        super(self.__class__, self).__init__(name, running)
        self.length = length
        self.grid = grid
        if self.grid == "":
            self.grid = self.make_game(self.length)
            self._insert_new_item()

    @staticmethod
    def make_game(length):
        return [[0 for x in range(length)] for y in range(length)]

    def keyboards(self):
        return self.keys

    def load(self, json_data):
        try:
            j = json.loads(json_data)
            return Game2048(**j)
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

    def start_game(self):
        return self._print_grid()

    def _print_grid(self):
        return ("\n|%s|\n" % "+".join([('-' * 4)] * self.length)).join(
            ["|%s|" % "|".join(["%6d" % item if item > 0 else "        " for item in line]) for line in self.grid])

    def run_game(self, user_input):
        direction = str(user_input).strip().lower()
        value = self._validate(direction)
        if value:
            return value

        if self._move(direction, False):
            msg = self._print_grid()
            msg += "\n 당신이 이겼습니다."
            self.end_game()
            return msg

        self._insert_new_item()
        return self._print_grid()

    def _validate(self, direction):
        movable_direction = self._get_movable_directions(direction)
        if len(movable_direction) == 0:
            self.end_game()
            msg = self._print_grid() + "\n당신이 졌습니다. %s 을 클릭하여 재시작 해 주세요." % self.ID
            return msg

        if direction not in movable_direction:
            msg = self._print_grid() + "\n %s 방향으로는 움직일 수 없습니다." % direction
            return msg

        return None

    def _get_movable_directions(self, direction):
        return [direction for direction in self.keys if self._move(direction, True)]

    def _insert_new_item(self):
        available_cells = self._get_available_cells()
        if len(available_cells) == 0:
            return False
        y, x = random.choice(available_cells)
        self.grid[y][x] = 2 if random.random() < 0.9 else self.length
        return True

    def _move(self, direction, virtual):
        r = self.length
        m = r - 1

        if direction == "left":  # left
            return any([self._merge_cells((i, 0), (i, 0), (0, 1), virtual) for i in range(r)])
        elif direction == "right":  # right
            return any([self._merge_cells((i, m), (i, m), (0, -1), virtual) for i in range(r)])
        elif direction == "up":  # up
            return any([self._merge_cells((0, i), (0, i), (1, 0), virtual) for i in range(r)])
        elif direction == "down":  # down
            return any([self._merge_cells((m, i), (m, i), (-1, 0), virtual) for i in range(r)])

    def _get_available_cells(self):
        r = self.length
        return [(y, x) for y in range(r) for x in range(r) if not self.grid[y][x]]

    def _is_legal_position(self, y, x):
        m = self.length - 1
        return 0 <= y <= m and 0 <= x <= m

    @staticmethod
    def _get_next_position(y, x, (y_offset, x_offset)):
        return y + y_offset, x + x_offset

    def _get_next_nonzero_cell(self, y, x, (y_offset, x_offset)):
        next_y, next_x = self._get_next_position(y, x, (y_offset, x_offset))
        if self._is_legal_position(next_y, next_x):
            if self.grid[next_y][next_x]:
                return next_y, next_x
            else:
                return self._get_next_nonzero_cell(next_y, next_x, (y_offset, x_offset))
        else:
            return None, None

    def _merge_cells(self, (write_y, write_x), (read_y, read_x), direction, virtual, winning=False):
        if (write_y, write_x) == (read_y, read_x):
            read_y, read_x = self._get_next_nonzero_cell(read_y, read_x, direction)
        if not self._is_legal_position(write_y, write_x) or not self._is_legal_position(read_y, read_x):
            return winning if not virtual else False
        if self.grid[write_y][write_x]:
            if self.grid[read_y][read_x] == self.grid[write_y][write_x]:
                if virtual:
                    return True
                self.grid[write_y][write_x] *= 2
                self.grid[read_y][read_x] = 0
                return self._merge_cells(self._get_next_position(write_y, write_x, direction),
                                         self._get_next_nonzero_cell(read_y, read_x, direction),
                                         direction, virtual, winning or self.grid[write_y][write_x] > 1024)
            else:
                return self._merge_cells(self._get_next_position(write_y, write_x, direction),
                                         (read_y, read_x), direction, virtual, winning)
        else:
            if virtual:
                return True
            self.grid[write_y][write_x] = self.grid[read_y][read_x]
            self.grid[read_y][read_x] = 0
            return self._merge_cells((write_y, write_x),
                                     self._get_next_nonzero_cell(read_y, read_x, direction),
                                     direction, virtual, winning)

def main():
    print "hello"
    g = Game2048()
    print g.start_game()
    while True:
        val = raw_input("?")
        msg = g.run_game(str(val))
        print msg

if __name__ == '__main__':
    main()
