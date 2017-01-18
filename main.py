#-*- coding: utf-8 -*-
#!/usr/bin/env python

import sys

import webapp2
import requests
import logging

import urllib
import urllib2
import json

from google.appengine.api import urlfetch
from model import GameRecord

from baseball import Baseball
from arithmetic import Arithmetic
from g2048 import Game2048

reload(sys)
sys.setdefaultencoding('utf-8')

DEBUG = False
DEBUG_URL = 'http://localhost/'

TOKEN = 'TOKEN'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

KEY = 0
VALUE = 1

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

###############################################################################
GAME_DIC = dict()
GAME_DIC[Baseball.INFO[KEY]] = Baseball.INFO[VALUE]
GAME_DIC[Arithmetic.INFO[KEY]] = Arithmetic.INFO[VALUE]
GAME_DIC[Game2048.INFO[KEY]] = Game2048.INFO[VALUE]
GAMES = GAME_DIC.keys()
###############################################################################


def make_markup(key, arrays):
    rtn = {key: [[]]}
    for arr in arrays:
        data = dict()
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
        inline_keyboard = make_markup('inline_keyboard', inline)
        params['reply_markup'] = inline_keyboard
    try:
        url = BASE_URL + 'sendMessage'
        logging.info(url)
        urllib2.urlopen(url, urllib.urlencode(params)).read()
    except Exception as e:
        logging.exception(e)


def edit_msg(msg_id, chat_id, text, no_preview=True, inline=None):
    params = {
        'chat_id': str(chat_id),
        'message_id' : str(msg_id),
        'text': text.encode('utf-8'),
        'disable_web_page_preview' : True
    }

    if inline:
        inline_keyboard = make_markup('inline_keyboard', inline)
        params['reply_markup'] = inline_keyboard
    try:
        url = BASE_URL + 'editMessageText'
        logging.info(url)
        res = urllib2.urlopen(url, urllib.urlencode(params)).read()
    except Exception as e:
        logging.exception(e)


def handle_start(text, game_record):
    if not CMD_START == text:
        return False

    game_record.set_enable(True)
    send_msg(game_record.key.id(), MSG_START)
    return True


def handle_stop(text, game_record):
    if not CMD_STOP == text:
        return False

    game_record.set_enable(False)
    send_msg(game_record.key.id(), MSG_STOP)
    return True


def handle_help(text, game_record):
    if not CMD_HELP == text:
        return False

    if not game_record.game:
        send_msg(game_record.key.id(), MSG_HELP, keyboard=CUSTOM_KEYBOARD)
        return True

    g = load_class(game_record.game)
    if not g:
        send_msg(game_record.key.id(), MSG_HELP, keyboard=CUSTOM_KEYBOARD)
        return

    g = g.load(game_record.record)
    send_msg(game_record.key.id(), g.help(), keyboard=CUSTOM_KEYBOARD)
    return True


def handle_list(text, game_record):
    if not CMD_LIST == text:
        return False

    send_msg(game_record.key.id(), "게임을 선택하세요.", inline=GAMES)
    return True


def select_game(text, game_record):
    g = load_class(str(text))
    if not g:
        logging.info('g is None')
        return False

    game_record.select_game(str(text), str(g))
    send_msg(game_record.key.id(), "%s 게임이 선택되었습니다." % g.get_name())
    send_msg(game_record.key.id(), g.start_game(), inline=g.keyboards())
    return True


def load_class(text):
    items = GAME_DIC.items()
    for index in range(len(items)):
        item = items[index]
        if text == item[KEY]:
            game_class = webapp2.import_string(item[VALUE])
            g = game_class()
            return g
    return None


def cmd_game(text, game_record):
    if not game_record:
        return

    if not game_record.game:
        return

    clazz = load_class(game_record.game)
    if not clazz:
        logging.info('clazz is None')
        return

    g = clazz.load(game_record.record)
    if not g:
        logging.info('g is None')
        return

    result = g.run_game(str(text))
    send_msg(game_record.key.id(), result, inline=g.keyboards())
    game_record.select_game(game_record.game, str(g))
    return

def cmd_edit(msg_id, text, game_record):
    if not game_record:
        return

    if not game_record.game:
        return

    clazz = load_class(game_record.game)
    if not clazz:
        logging.info('clazz is None')
        return

    g = clazz.load(game_record.record)
    if not g:
        logging.info('g is None')
        return

    result = g.run_game(str(text))

    edit_msg(msg_id, game_record.key.id(), result, inline=g.keyboards())
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
    return


def process_callbacks(msg):
    message = msg['message']
    msg_id = message['message_id']
    chat_id = message['chat']['id']
    text = message.get('text')
    data = msg['data']
    if not data:
        return

    game_record = GameRecord.get_record(chat_id)
    if not game_record.enabled:
        return

    if data.startswith('/'):
        select_game(data, game_record)
        return

    cmd_edit(msg_id, data, game_record)
    return


def request_debug(msg):
    requests.get(DEBUG_URL + 'debug?' + msg)
    return


class DebugHandler(webapp2.RequestHandler):
    def get(self):
        if DEBUG:
            logging.debug(self.request.body)
        return


class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))
        return


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))
        return


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))
        return


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        # request_debug(self.request.body)
        if DEBUG:
            logging.info(self.request.body)

        body = json.loads(self.request.body)
        self.response.write(json.dumps(body))
        if 'message' in body:
            process_cmds(body['message'])

        if 'callback_query' in body:
            process_callbacks(body['callback_query'])
        return


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set-webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/debug', DebugHandler),
], debug=True)
