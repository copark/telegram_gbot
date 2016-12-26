
from google.appengine.ext import ndb
import logging

class GameRecord(ndb.Model):
    enabled = ndb.BooleanProperty(required=True, indexed=True, default=False,)
    game = ndb.StringProperty()
    record = ndb.StringProperty()

    @staticmethod
    def get_record(chat_id):
        return GameRecord.get_or_insert(str(chat_id))

    @staticmethod
    def set_record(chat_id, enabled):
        game_record = GameRecord.get_or_insert(str(chat_id))
        game_record.enabled = enabled
        game_record.put()

    def set_enable(self, enabled):
        self.enabled = enabled
        self.put()

    def select_game(self, game, record):
        self.game = game
        self.record = record
        self.put()