#-*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from google.appengine.api import urlfetch

import webapp2
import requests
import logging

import urllib
import urllib2
import json

from model import GameRecord
from game import Game
from baseball import Baseball

DEBUG = True
DEBUG_URL = 'http://localhost/'

TOKEN = 'TOKEN'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

CMD_START   = '/start'
CMD_STOP    = '/stop'
CMD_HELP    = '/help'
CMD_LIST    = '/listgames'

MSG_START       = "게임을 시작합니다. /listgames 으로 게임을 선택하세요."
MSG_STOP        = "게임을 종료합니다."
MSG_HELP        = "도움말 입니다."

CUSTOM_KEYBOARD = [
        [CMD_START, CMD_STOP],
        [CMD_HELP, CMD_LIST],
        ]

BASEBALL = '/baseball'
GAMES = [BASEBALL]
GAME_DIC = {'/baseball': 'baseball.Baseball'}

def make_markup(key, ARRAYS):
    rtn = {key: [[]]}
    for arr in ARRAYS:
        data = {}
        data['callback_data'] = arr
        data['text'] = arr
        rtn['inline_keyboard'][0].append(data)

    return json.dumps(rtn)

def send_msg(chat_id, text, reply_to=None, no_preview=True, keyboard=None, inline=None):
    params = {
        'chat_id': str(chat_id),
        'text': text.encode('utf-8'),
        }
    if reply_to:
        params['reply_to_message_id'] = reply_to
    if no_preview:
        params['disable_web_page_preview'] = no_preview
    if keyboard:
        reply_markup = json.dumps({
            'keyboard': keyboard,
            'resize_keyboard': True,
            'one_time_keyboard': False,
            'selective': (reply_to != None),
            })
        params['reply_markup'] = reply_markup
    if inline:
        inline_keyboard = make_markup('inline_keyboard', GAMES)
        params['reply_markup'] = inline_keyboard
        logging.info(inline_keyboard)
    try:
        urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params)).read()
    except Exception as e:
        logging.exception(e)

def handle_start(text, game_record):
    if CMD_START == text:
        game_record.set_enable(True)
        send_msg(game_record.key.id(), MSG_START)
        return True
    return False

def handle_stop(text, game_record):
    if CMD_STOP == text:
        game_record.set_enable(False)
        send_msg(game_record.key.id(), MSG_STOP)
        return True
    return False

def handle_help(text, game_record):
    if CMD_HELP == text:
        send_msg(game_record.key.id(), MSG_HELP, keyboard=CUSTOM_KEYBOARD)
        return True
    return False

def handle_list(text, game_record):
    if CMD_LIST == text:
        send_msg(game_record.key.id(), "게임을 선택하세요.", inline=GAMES)
        return True
    return False

def select_game(text, game_record):
    for _game in GAMES:
        if text == _game:
            g = load_game(str(_game))
            game_record.select_game(str(_game), str(g))
            send_msg(game_record.key.id(), str(_game) + " 게임이 선택되었습니다.")
            send_msg(game_record.key.id(), g.info())
            return True
    return False

def load_game(text):
    if text == BASEBALL:
        str = Baseball.make_game()
        g = Baseball(str)
        return g
    return None

def cmd_game(text, game_record):
    if not game_record:
        return

    if not game_record.game:
        return

    g = Baseball.load_from_json(game_record.record)
    logging.info(game_record.record)

    if not g:
        logging.info('g is None')
        return

    result = g.run_game(str(text))
    send_msg(game_record.key.id(), result)
    game_record.select_game(game_record.game, str(g))
    return

def process_cmds(msg):
    msg_id = msg['message_id']
    chat_id = msg['chat']['id']
    text = msg.get('text')
    if not text:
        return

    game_record = GameRecord.get_record(chat_id)

    if handle_start(text, game_record):
        return

    if handle_stop(text, game_record):
        return

    if not game_record.enabled:
        return

    if handle_help(text, game_record):
        return

    if handle_list(text, game_record):
        return
    
    if select_game(text, game_record):
        return

    cmd_game(text, game_record)

def process_callbacks(msg):
    message = msg['message']
    msg_id = message['message_id']
    chat_id = message['chat']['id']
    text = message.get('text')
    data = msg['data']
    if not data:
        return

    game_record = GameRecord.get_record(chat_id)
    select_game(data, game_record)

def request_debug(msg):
    requests.get(DEBUG_URL + 'debug?' + msg)

class DebugHandler(webapp2.RequestHandler):
    def get(self):
        if DEBUG:
            logging.debug(self.request.body)

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))

class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))

class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        request_debug(self.request.body)
        body = json.loads(self.request.body)
        self.response.write(json.dumps(body))
        if 'message' in body:
            process_cmds(body['message'])

        if 'callback_query' in body:
            process_callbacks(body['callback_query'])

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set-webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/debug', DebugHandler),
], debug=True)
