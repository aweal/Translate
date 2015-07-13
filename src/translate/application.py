#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gio
import os
import sys

sys.path.append(os.path.dirname(__file__))

import guigetkey
from guitranslatewnd import MainWnd

from setting import SettingManager
from wingeometry import Pos
from wingeometry import Size
from timer import Timer
from yatranslate import TranslateIt

import logging
import argparse
import yatranslate



class TransApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self,
                                 flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.lgr = logging.getLogger('')
        self.settings = SettingManager()
        self._translator = TranslateIt(self.settings.yandex_api_key)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if self.create_main_wnd():
            self.ok_run()
        else:
            self.show_get_apikey_dialog()

    def do_command_line(self, args):
        Gtk.Application.do_command_line(self, args)

        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='set logger level to verbose')
        args = parser.parse_args(args.get_arguments()[1:])

        if args.verbose:
            print('DEBUG mode on..')
            self.create_logger(logging.DEBUG)
        else:
            self.create_logger()

        self.do_activate()
        return 0

    def do_shutdown(self):
        exit(0)

    def ok_run(self):
        self.timer.start()
        self.load_other_settings()

        if self.settings.single_mode:
            self.lgr.debug('Single mode = True')
            self.win.clipboard_primary_status = not self.settings.switch
            self.win.clipboard_selection_status = self.settings.switch

        else:
            self.win.clipboard_primary_status = not self.settings.switch
            self.win.clipboard_selection_status = True

    def msg_dialog_global_err(self):
        dialog = Gtk.MessageDialog(transient_for=self.win,
                                   destroy_with_parent=True,
                                   message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.OK,
                                   modal=True,
                                   text="Connection aborted: Temporary failure in name resolution")
        dialog.run()
        dialog.destroy()

    def show_get_apikey_dialog(self):
        self.key_wnd = guigetkey.GeTokenWnd(self)
        self.key_wnd.wnd.set_transient_for(self.win)
        self.key_wnd.wnd.set_modal(True)
        self.key_wnd.wnd.connect("response", self.get_api_dialog_response)
        self.key_wnd.wnd.show_all()

    def get_api_dialog_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            key = self.key_wnd.edit.get_text()
            if not self.settings.keyIsValid(key):
                self.lgr.debug('The key "%s" is not passed server validation', key)
                self.key_wnd.show_error('invalid key!')
                return 0
            else:
                # 3 time key_valid run!
                self.settings.yandex_api_key = key
                self._translator.key = key
                self.ok_run()
        else:
            self.quit()
        widget.destroy()

    # timer use there!
    def timer_start(self):
        self.timer.work = True

    def timer_stop(self):
        self.timer.work = False

    def timer_halt(self):
        self.timer.work = False
        self.timer.halt()

    def translate(self, txt):
        if len(txt) > 1:
            return self._translator.translate(txt)
        else:
            self.lgr.debug('skip text (len <=1)')

    def create_logger(self, level=logging.ERROR):
        ch = logging.StreamHandler()
        formt = logging.Formatter('%(levelname)s: \t%(asctime)s | %(process)d | %(lineno)d: '
                                  '%(module)s.%(funcName)s | %(name)s  | %(message)s')
        ch.setFormatter(formt)

        self.lgr.setLevel(level)
        ch.setLevel(level)

        self.lgr.addHandler(ch)
        self.lgr.info('Load logger done: ')

    # timer call back fn:
    def callback_end_time(self):
        """callback for timer"""
        self.win.pb.set_visible(False)

        if not self.win.clipboard_primary_status:
            self.lgr.debug('Clipboard primary disable...')
            return False
        txt = self.win.primary_text

        if len(txt) < 1:
            self.lgr.debug('The text is too short: %s`', txt)
            return False

        answer = self.translate(txt)
        self.win.translated_primary_text = answer

    # timer tick call back:
    def call_back_pulse(self):
        self.win.pb.pulse()

    # settings:
    def load_other_settings(self):
        self.win.single_mode = self.settings.single_mode
        if self.win.single_mode:
            self.act_view_behavior_single.activate()

        if self.win.switch.get_state() == self.settings.switch:
            # on  switch setup: clipboard_primary_status /clipboard_selection_status
            self.win.on_switch_change(self.win.switch, None)
        else:
            self.win.switch.set_state(self.settings.switch)

    def load_window_geometry(self):
        pos_from_setting = self.settings.window_position
        self.lgr.debug('Set window position `%d`x`%d` ', pos_from_setting.TOP, pos_from_setting.LEFT)
        self.win.move(pos_from_setting.TOP, pos_from_setting.LEFT)

        size_from_setting = self.settings.window_size
        self.lgr.debug("Set window size `%d`x`%d` ", size_from_setting.WIDTH, size_from_setting.HEIGHT)
        self.win.set_default_size(size_from_setting.WIDTH, size_from_setting.HEIGHT)

    def save_settings(self):
        current_win_pos = self.win.get_position()
        _pos = Pos(current_win_pos[0], current_win_pos[1])
        self.lgr.info('save windows position: %d x %d', _pos.TOP, _pos.LEFT)
        self.settings.window_position = _pos

        current_win_size = self.win.get_size()
        _size = Size(current_win_size[0], current_win_size[1])
        self.lgr.info('windows size to save: %d x %d', _size.WIDTH, _size.HEIGHT)
        self.settings.window_size = _size

        self.settings.single_mode = self.win.single_mode
        self.settings.switch = self.win.switch.get_active()
        self.settings.saveConfig()

    # actions:
    def on_close_mainwnd(self, *args):
        self.act_quit.activate()

    def act_quit_execute(self, action, parameter):
        self.timer_halt()
        self.save_settings()
        self.quit()

    # velodrome
    def view_behavior_all(self, act, *args):
        self.gsubmenu.remove_all()
        self.gsubmenu.append('* all', "app.view_all")
        self.gsubmenu.append('single', "app.view_single")
        self.win.single_mode = False

    def view_behavior_single(self, act, *args):
        self.gsubmenu.remove_all()
        self.gsubmenu.append('all', "app.view_all")
        self.gsubmenu.append('* single', "app.view_single")
        self.win.single_mode = True

    # GUI:
    def create_main_wnd(self):
        """
        Create Main window
            :return: True if yandex api key is valid
        """
        self.win = MainWnd(self)

        self.add_window(self.win)
        self.menu_main = Gio.Menu()
        self.gsubmenu = Gio.Menu()

        self.menu_main.append_submenu('show', self.gsubmenu)
        # self.radio_all = True -> * show all esle show single
        self.gsubmenu.append('* all', "app.view_all")
        self.gsubmenu.append('single', "app.view_single")

        self.menu_main.append("About", "app.about")
        self.menu_main.append("_____________")
        self.menu_main.append("Quit", "app.quit")

        self.set_app_menu(self.menu_main)

        self.timer = Timer(self.callback_end_time, self.call_back_pulse)

        self.win.connect("delete_event", self.on_close_mainwnd)

        self.act_view_behavior_all = Gio.SimpleAction.new("view_all", None)
        self.act_view_behavior_all.connect("activate", self.view_behavior_all)
        self.add_action(self.act_view_behavior_all)

        self.act_view_behavior_single = Gio.SimpleAction.new("view_single", None)
        self.act_view_behavior_single.connect("activate", self.view_behavior_single)
        self.add_action(self.act_view_behavior_single)

        self.act_about = Gio.SimpleAction.new("about", None)
        self.act_about.connect("activate", self.win.act_about_execute)
        self.add_action(self.act_about)

        self.act_quit = Gio.SimpleAction.new("quit", None)
        self.act_quit.connect("activate", self.act_quit_execute)
        self.add_action(self.act_quit)

        self.load_window_geometry()
        self.win.show_all()

        status_key = self.settings.keyIsValid(self.settings.yandex_api_key)

        if status_key:
            if status_key == yatranslate.ERR_CONNECTION_ABORTED:
                self.lgr.error('Cannot connect to server, exit..')
                self.msg_dialog_global_err()
                sys.exit(0)
            return True

        return False


def run():
    app = TransApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == '__main__':
    run()
