#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import logging
import os.path
from yatranslate import TranslateIt
from wingeometry import Pos
from wingeometry import Size

_LINK_YA_IPI = "http://api.yandex.ru/key/form.xml?service=trnsl"
_VERSION = "0.3"
_DEFAULT_CONFIG = dict(_VERSION="0.2", API_KEY="", POS_TOP=778, POS_LEFT=380,
                       WIDTH=400, HEIGHT=100, SWITCH=0, SHOW_ALL=0)


class SettingManager:
    def __init__(self):
        self.lgr = logging.getLogger('setting')
        self.trans = TranslateIt('')
        self.__ROOT_CFG_PATH = os.path.expanduser("~")
        self.__CONFIG_NAME = ".trans"
        self.__config = _DEFAULT_CONFIG

        self.check_path()

        if self.loadConfig():
            if self.keyIsValid(self.yandex_api_key):
                self.status_key = True
            else:
                self.status_key = False

    def check_path(self):
        if not os.path.exists(self.__ROOT_CFG_PATH):
            raise OSError(2, 'No such file or directory')
        if not os.path.isdir(self.__ROOT_CFG_PATH):
            raise Exception('Invalid config path')

        if not os.access(self.__ROOT_CFG_PATH, os.W_OK):
            raise Exception('Access wrote in path fail')

        if not os.path.exists(self.config_name):
            self.lgr.warning('No config file try create: ')
            self.saveConfig()
            # raise Exception('No config file!')
        return True

    @property
    def config_name(self):
        return self.__ROOT_CFG_PATH + '/' + self.__CONFIG_NAME

    @config_name.setter
    # @debug
    def config_name(self, new_name):
        """
        ONLY FOR DEBUG!
        :param new_name: string  $HOME full path cfg is($HOME + /.trans)
        :return:
        """
        # set invalid name!
        self.__ROOT_CFG_PATH = new_name

    def get_cfg_value(self, key):
        if key not in self.config:
            self.lgr.error("No key '%s' in config... ", key)
            # warning!
            return None
        else:
            return self.config[key]

    def set_cfg_value(self, key, val):
        if val is None:
            self.lgr.error("Skip null value for key %s", key)
            return False

        if key not in self.config:
            if key in _DEFAULT_CONFIG:
                self.lgr.debug('CFG without key %s - add new', key)
                self.config[key] = val
                return True
            else:
                self.lgr.error('Key %s invalid for $VERSION: %s', key, _VERSION)
                return False
        else:
            self.config[key] = val
            return True

    @property
    def config(self):
        """
        setup cfg from config file
        :return: dict{} example see _DEFAULT_CONFIG
        """
        if self.__config is None:
            self.lgr.error("config is None... halt?...")
        return self.__config

    @config.setter
    def config(self, cfg):
        if cfg is not None:
            self.__config = cfg

    @property
    def window_size(self):
        """
        Setup main wnd size width and height
            :return: wingeometry.Size()
        """
        return Size(self.get_cfg_value('WIDTH'), self.get_cfg_value('HEIGHT'))

    @window_size.setter
    def window_size(self, _size):
        if not type(_size) is Size:
            self.lgr.debug("The Size param required  '%s' received ", type(_size))
            raise ValueError()

        if not self.set_cfg_value('WIDTH', _size.WIDTH):
            self.lgr.warning("Fail save width window...")

        if not self.set_cfg_value('HEIGHT', _size.HEIGHT):
            self.lgr.warning("Fail save HEIGHT window...")

    @property
    def window_position(self):
        """
        Setup Position Main window (TOP / LEFT)
            :return: wingeometry.Pos()
        """
        return Pos(self.get_cfg_value('POS_TOP'), self.get_cfg_value('POS_LEFT'))

    @window_position.setter
    def window_position(self, new_pos):
        if not self.set_cfg_value('POS_TOP', new_pos.TOP):
            self.lgr.warning("Failed save '%d' top position window ", new_pos.TOP)

        if not self.set_cfg_value('POS_LEFT', new_pos.LEFT):
            self.lgr.warning("Failed save '%d' top position window ", new_pos.LEFT)

    @property
    def switch(self):
        """
        Store status switch in setting
            :return: Boolean True / False
        """
        switch = self.get_cfg_value('SWITCH')

        if switch is not None:
            type_val = type(switch)
            if type_val is bool:
                return self.get_cfg_value('SWITCH')
            else:
                self.lgr.error('Wrong type of switch `%s`, Boolean required!', type_val)
        else:
            self.lgr.error('Switch not determined in the configuration file')
        # by default
        return False

    @switch.setter
    def switch(self, state=0):
        self.set_cfg_value('SWITCH', state)

    @property
    def single_mode(self):
        """
        store View All / Single
            :return: Boolean True / False
        """
        show_all = self.get_cfg_value('SHOW_ALL')
        if show_all is not None:
            if type(show_all) is bool:
                return show_all
            else:
                self.lgr.debug('wrong cfg value, use default')

        return False

    @single_mode.setter
    def single_mode(self, state):
        self.set_cfg_value('SHOW_ALL', state)

    @property
    def yandex_api_key(self):
        """
        Store yandex Key need for translation
            :return: string
        """
        return self.get_cfg_value('API_KEY')

    @yandex_api_key.setter
    def yandex_api_key(self, __key):
        if not self.keyIsValid(__key):
            raise ValueError('Invalid key API')
        else:
            self.set_cfg_value('API_KEY', __key)
        self.saveConfig()

    def keyIsValid(self, __key):
        return self.trans.valid_key(__key)

    def loadConfig(self):
        self.lgr.debug('load from %s', self.config_name)
        config_name = self.config_name

        try:
            if not os.path.exists(config_name):
                self.lgr.debug('File "%s" doesnt exist...', config_name)
                return False

            with open(config_name, 'r') as f:
                config = json.load(f)
        except Exception as err:
            self.lgr.exception('Failed load "%s" cfg: %s',
                               config_name, err)
            return False

        if config is not None:
            self.config = config
        else:
            self.lgr.error('Error load setting!')
        return True

    def saveConfig(self):
        self.lgr.debug('Save config %s', self.config_name)

        try:
            with open(self.config_name, 'w') as f:
                status = json.dump(self.config, f)
        except Exception as err:
            self.lgr.exception('Failed save "%s": %s ',
                               self.config_name, err)
            return False

        return True
