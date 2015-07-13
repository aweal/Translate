#!/usr/bin/python3
# -*- coding: utf-8 -*-


import unittest
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               '../src/translate')))

from src.translate.setting import SettingManager

from src.translate.wingeometry import Size, Pos


lgr = logging.getLogger('')

ch = logging.StreamHandler()
formt = logging.Formatter('%(levelname)s: \t%(asctime)s | %(process)d | %(lineno)d: %(module)s.%(funcName)s | '
                                  '%(name)s  | %(message)s')
ch.setFormatter(formt)

lgr.setLevel(logging.DEBUG)
ch.setLevel(logging.DEBUG)
lgr.addHandler(ch)


class TestSettingManager(unittest.TestCase):
    def setUp(self):
        self.lgr = logging.getLogger('test.SettingManager')
        self.lgr.debug('log start!')
        self.sm = SettingManager()

    def test_wrong_path_on_load_setting(self):
        self.lgr.info("start test: with path cfg: /root1/.trans  ...")
        self.sm.config_name = '/root1'
        self.assertFalse(self.sm.loadConfig())

    def test_wrong_permission_on_load_setting(self):
        # при ошибке доступа сообщает что нет файла фичебаг?
        self.lgr.info("start test: load setting file without permissions ...")
        self.sm.config_name = '/root'

        self.assertFalse(self.sm.loadConfig())

    def test_no_config_on_load_setting_file(self):
        self.lgr.info("start test: no cfg file:..")
        self.sm.config_name = "/tmp"
        self.assertTrue(self.sm.saveConfig())

    def test_wrong_permission_on_save_setting(self):
        self.lgr.info("start test save cfg file without permissions ... Or u root?")
        self.sm.config_name = '/root'
        self.assertFalse(self.sm.saveConfig())

    def test_nospace_on_save_setting(self):
        self.lgr.info("start test: no space start...")
        # tmpfs	/tmp/dbg	tmpfs   users,nodev,nosuid,noexec,size=1m 0 0
        # mkdir /tmp/dbg && sudo mount -t tmpfs -o size=1m tmpfs /tmp/dbg/; cat /dev/urandom > /tmp/dbg/full.log

        # try:
        #    subprocess.call("mkdir /tmp/dbg/; touch /tmp/dbg/.trans", shell=True)
        #    subprocess.call("mount /tmp/dbg", shell=True)
        #    subprocess.call("cat /dev/urandom > /tmp/dbg/full.log", shell=True)
        # finally:
        #    subprocess.call("umount /tmp/dbg", shell=True)

        self.sm.config_name = '/tmp/dbg'
        self.assertFalse(self.sm.saveConfig())

    def test_window_size_not_int(self):
        self.lgr.info("start test: set window size  not int")

        with self.assertRaises(ValueError):
            self.sm.window_size = 'Oops'

    def test_size_not_int_val(self):
        self.lgr.info("start test: set Size  not int")

        sz = Size('OOPS', 200)
        self.assertEqual(sz.WIDTH, 400)

    def test_window_size_subzero_param(self):
        self.lgr.info("start test: with invalid Size param")

        sz = Size(-1, 230)
        self.assertEqual(sz.WIDTH, 400)

    def test_win_pos_not_pos_param(self):
        self.lgr.info("start test: try set win pos with invalid params")

        pos = Pos(-3, 0)
        self.assertEqual(pos.TOP, 400)
        pos = Pos()
        self.assertEqual(pos.TOP, 400)
        pos = Pos('Noway')
        self.assertEqual(pos.TOP, 400)

    def test_prop_yandex_api_key(self):
        self.lgr.info("start test: try get valuet from null cgf: example yandext_api_key")
        self.sm.config = {}
        # KeyError
        self.assertFalse(self.sm.yandex_api_key)
        with self.assertRaises(ValueError):
            self.sm.yandex_api_key = "Not none"
        # self.assertFalse(self.sm.set_cfg_value('API_KEY', 'Not None'))

    def test_null_return(self):
        #
        self.lgr.info("start test: отличия 0 от False?")
        self.sm.config = dict(POS_TOP=0, POS_LEFT=0)

        self.assertEqual(self.sm.get_cfg_value('POS_TOP'), 0)

    #
    # по порядку:
    #

    def test_check_path_invalid_dir(self):
        self.lgr.info('start test: check path with invalid dir')
        self.sm.config_name = '/tmp-nodir'
        with self.assertRaises(OSError):
            self.sm.check_path()

    def test_check_path_not_dir(self):
        self.lgr.info('start test: check path is dir?')
        self.sm.config_name = '/etc/fstab'
        with self.assertRaises(Exception):
            self.sm.check_path()

    def test_set_cfg_value_nokey(self):
        self.lgr.info('start test: set_cfg_value no key ...')
        self.sm.config = dict(invalid_key=0)
        self.assertFalse(self.sm.set_cfg_value('nokey', 1))

    def test_set_cfg_value_non_key(self):
        self.lgr.info('start test: set_cfg_value with None key ...')
        self.assertFalse(self.sm.set_cfg_value(None, 1))

    def test_set_cfg_value_non_value(self):
        self.lgr.info('start test: set_cfg_value with None value ...')
        self.assertFalse(self.sm.set_cfg_value('asdf', None))

    def test_gettr_window_size_noconfig(self):
        self.lgr.info('start test: config without width / height')
        # wrong config values:
        self.sm.config = dict(_WIDTH=0, _HEIGHT=0)
        # must be a default:
        self.assertEqual(self.sm.window_size.WIDTH, 400)
        self.assertEqual(self.sm.window_size.HEIGHT, 200)

    def test_gettr_window_size_config_wrong_param_float(self):
        self.lgr.info('start test: config with float width / height')
        self.sm.config = dict(WIDTH=1.0, HEIGHT=0.5)

        self.assertEqual(self.sm.window_size.WIDTH, 400)
        self.assertEqual(self.sm.window_size.HEIGHT, 200)

    def test_gettr_window_size_zero_config_vall(self):
        self.lgr.info('start test: 0 value return True! not False;)')
        self.sm.config = dict(WIDTH=0, HEIGHT=0)

        self.assertEqual(self.sm.window_size.WIDTH, 0)
        self.assertEqual(self.sm.window_size.HEIGHT, 0)

    def test_gettr_window_size_config_null_values(self):
        self.lgr.info('start test: check None in cfg:')
        self.sm.config = dict(WIDTH=None, HEIGHT=None)

        self.assertEqual(self.sm.window_size.WIDTH, 400)
        self.assertEqual(self.sm.window_size.HEIGHT, 200)

    def test_settr_window_size_noconfig(self):
        self.lgr.info('start test: set config without width / height')
        self.sm.config = dict(_WIDTH=0, _HEIGHT=0)

        self.sm.window_size = Size(10, 20)
        self.assertEqual(self.sm.window_size.WIDTH, 10)
        self.assertEqual(self.sm.window_size.HEIGHT, 20)

    def test_settr_window_size_wrong_size_param(self):
        self.lgr.info('start test: sett windows size with wrong Size values')
        # all test where:
        self.sm.window_size = Size(None, -10)
        # DEFAULT:
        self.assertEqual(self.sm.window_size.WIDTH, 400)
        self.assertEqual(self.sm.window_size.HEIGHT, 200)

        self.sm.window_size = Size(True, None)
        # DEFAULT:
        self.assertEqual(self.sm.window_size.WIDTH, 400)
        self.assertEqual(self.sm.window_size.HEIGHT, 200)

        self.sm.window_size = Size(0.5, self)

        self.assertEqual(self.sm.window_size.WIDTH, 400)
        self.assertEqual(self.sm.window_size.HEIGHT, 200)

    def test_gettr_window_position(self):
        self.lgr.info('Start test getter window_position')

        self.lgr.info('Check cfg zero not False!')
        self.sm.config = dict(POS_TOP=0, POS_LEFT=0)

        self.assertEqual(self.sm.window_position.TOP, 0)
        self.assertEqual(self.sm.window_position.LEFT, 0)

        self.lgr.info('Check cfg with wrong  POS_x ')

        self.sm.config = dict(POS_TOPx=0, POS_LEFT=None)
        self.assertEqual(self.sm.window_position.TOP, 400)
        self.assertEqual(self.sm.window_position.LEFT, 200)

        self.sm.config = dict(POS_TOP=-50, POS_LEFT=False)
        self.assertEqual(self.sm.window_position.TOP, 400)
        self.assertEqual(self.sm.window_position.LEFT, 200)

    def test_settr_window_position(self):
        self.lgr.info('Start test with setter window_position')

        self.sm.window_position = Pos(-1, None)
        self.assertEqual(self.sm.window_position.TOP, 400)
        self.assertEqual(self.sm.window_position.LEFT, 200)

        self.sm.window_position = Pos(0, 0)
        self.assertEqual(self.sm.window_position.TOP, 0)
        self.assertEqual(self.sm.window_position.LEFT, 0)

        self.sm.window_position = Pos(1.1, self)
        self.assertEqual(self.sm.window_position.TOP, 400)
        self.assertEqual(self.sm.window_position.LEFT, 200)

    def test_getter_switch(self):
        self.lgr.info('Starts test getter switch')
        self.sm.config = dict(SWITCH_='')
        self.assertFalse(self.sm.switch)

        self.sm.config = dict(SWITCH=0)
        self.assertFalse(self.sm.switch)

        self.sm.config = dict(SWITCH=None)
        self.assertFalse(self.sm.switch)

        self.sm.config = dict(SWITCH=-1)
        self.assertFalse(self.sm.switch)

        self.sm.config = dict(SWITCH=10)
        self.assertFalse(self.sm.switch)

        self.sm.config = dict(SWITCH=1)
        self.assertFalse(self.sm.switch)

        self.sm.config = dict(SWITCH=True)
        self.assertTrue(self.sm.switch)

        self.sm.config = dict(SWITCH=-1)
        self.assertEqual(type(self.sm.switch), bool)

        self.sm.config = dict(SWITCH=1)
        self.assertFalse(self.sm.switch)

        self.sm.config = dict(SWITCH=0)
        self.assertFalse(self.sm.switch)

        self.sm.config = dict(SWITCH=True)
        self.assertTrue(self.sm.switch)

    def test_setter_switch(self):
        self.lgr.info('Start tests setter switch')

        self.sm.switch = True
        # def value:
        self.assertTrue(self.sm.switch)

        self.sm.switch = 0
        self.assertFalse(self.sm.switch)

        self.sm.switch = -1
        self.assertFalse(self.sm.switch)

    def test_gettr_single_mode(self):
        self.lgr.info('Start tests getter switch')

        self.sm.config = dict(SHOW_ALL=-1)
        self.assertEqual(type(self.sm.single_mode), bool)

        self.sm.config = dict(NO_SHOW_ALL=1)
        self.assertFalse(self.sm.single_mode)

        self.sm.config = dict(SHOW_ALL=0)
        self.assertFalse(self.sm.single_mode)

        self.sm.config = dict(SHOW_ALL=1)
        self.assertFalse(self.sm.single_mode)

        self.sm.config = dict(SHOW_ALL=True)
        self.assertTrue(self.sm.single_mode)

    def test_settr_single_mode(self):
        self.lgr.info('Start tests setter switch')
        self.sm.config = dict(NO_SHOW_ALL=0)

        self.sm.single_mode = 1
        self.assertFalse(self.sm.single_mode)

        self.sm.config = dict(SHOW_ALL='wrong type')
        self.assertFalse(self.sm.single_mode)

        self.sm.config = dict(SHOW_ALL=10)
        self.assertFalse(self.sm.single_mode)

        self.sm.config = dict(SHOW_ALL=0)
        self.assertFalse(self.sm.single_mode)

        self.sm.config = dict(SHOW_ALL=1)
        self.assertFalse(self.sm.single_mode)

    def test_gettr_yakey(self):
        self.lgr.info('start test: gettr ya key')
        self.sm.config = dict(NO_API_KEY='No key')

        self.assertFalse(self.sm.yandex_api_key)

        self.sm.config = dict(API_KEY='some_key')
        self.assertEqual(self.sm.yandex_api_key, 'some_key')

    def test_save_cfg_wrong_permission(self):
        self.lgr.info('start test: save cfg wrong permission')

        self.sm.config_name = '/sys'
        self.sm.config = dict(SOME='KEY')
        self.assertFalse(self.sm.saveConfig())

    def test_save_cfg_no_space(self):
        self.lgr.info('start test: No space')
        self.sm.config_name = '/tmp/dbg'
        #print(self.sm.saveConfig())
        self.assertFalse(self.sm.saveConfig())

    def test_save_cfg_in_tmp(self):
        # mb save in home?
        self.lgr.info('start test: simple save')
        self.sm.config_name = '/tmp'
        self.sm.config = dict(SOME='KEY')

        self.assertTrue(self.sm.saveConfig())

"""
def test_(self):
    self.lgr.info('start test:')

"""

if __name__ == "__main__":
    unittest.main()
