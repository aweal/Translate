#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
import logging

_URL_JSONPOST = "https://translate.yandex.net/api/v1.5/tr.json/translate"

ERR_OK = 200
ERR_KEY_INVALID = 401
ERR_KEY_BLOCKED = 402
ERR_DAILY_REQ_LIMIT_EXCEEDED = 403
ERR_DAILY_CHAR_LIMIT_EXCEEDED = 404
ERR_TEXT_TOO_LONG = 413
ERR_UNPROCESSABLE_TEXT = 422
ERR_LANG_NOT_SUPPORTED = 501

ERR_CONNECTION_ABORTED = -1


class TranslateIt:
    def __init__(self, key):
        self._key = key
        self.lgr = logging.getLogger('yatrans')

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new_key):
        if self.valid_key(new_key):
            self.lgr.debug('Setup new yandex key')
            self._key = new_key
        else:
            self.lgr.debug('invalid key!')

    def valid_key(self, key):
        try:
            r = requests.get(url="https://translate.yandex.net/api/v1.5/tr.json/getLangs",
                             params=dict(key=key, ui='ru'))

        except Exception as Err:
            # trace  1 Km:
            # self.lgr.exception("Connection error %s", Err)
            print("ERR: ", Err)
            return ERR_CONNECTION_ABORTED

        answer = r.json()
        if 'code' in answer:
            self.lgr.error('Test key failed: %d, %s', answer['code'], answer['message'])
            return False
        else:
            return True

    def translate(self, txt):
        data = dict(key=self._key, lang='en-ru', text=txt)
        try:
            r = requests.get(url=_URL_JSONPOST, params=data)
        except ConnectionError as err:
            self.lgr.exception('Connection error: %s', str(err))
            return ERR_CONNECTION_ABORTED

        self.lgr.debug("RESPONSE: %s", r)
        answer = r.json()
        self.lgr.debug("ANSWER: %s", answer)
        if 'code' in answer:
            if answer['code'] == ERR_OK:
                self.lgr.debug('Translated text: `%s`',  ' '.join(answer['text']))
                return ' '.join(answer['text'])
            elif answer['code'] == ERR_KEY_INVALID:
                self.lgr.debug('Invalid yandex api key: `$s`', self._key)
        return False
