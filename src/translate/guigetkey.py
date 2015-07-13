#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from gi.repository import Gtk


_MSG_WRONG_KEY = """<span color="red">Hint: </span> You can get the API key on \
<a href="https://tech.yandex.com/keys/get/?service=trnsl%3Fservice%3Dtrnsl" \
title="Get API Key">this page</a>, also you can check status or choose \
<a href="https://tech.yandex.com/keys/?service=trnsl" title="My keys">previously created</a> \n  """

_MSG_ERROR = """<big><span color='red'>ERROR:  </span> </big>"""


class GeTokenWnd(Gtk.ApplicationWindow):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.lgr = self.lgr = logging.getLogger('getkey')
        self.wnd = Gtk.Dialog(title='I need you clothes, your boots and your api key')
        self.wnd.set_application(self.app)
        self.wnd.set_keep_above(True)
        self.wnd.set_default_size(500, 200)
        self.wnd.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.NONE)
        self.wnd.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        lbl = Gtk.Label("Enter you api key there:")
        self.edit = Gtk.Entry()
        self.content_area = self.wnd.get_content_area()
        self.content_area.pack_end(self.edit, True, True, 0)
        self.content_area.pack_end(lbl, True, True, 0)
        self.infobar = None

    def show_error(self, msg):
        if self.infobar is None:
            self.infobar = Gtk.InfoBar()
            self.infobar.connect("response", self.infobar_response)
            self.infobar.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
            # self.infobar.set_show_close_button(True)
            self.infobar.set_default_response(Gtk.ResponseType.CLOSE)

            self.infobar.set_message_type(Gtk.MessageType.ERROR)

            self.infobar.lbl_info = Gtk.Label(label=_MSG_WRONG_KEY)
            self.infobar.lbl_info.set_use_markup(True)
            self.infobar.lbl = Gtk.Label(label=_MSG_ERROR + msg)

            self.infobar.lbl.set_use_markup(True)
            self.infobar.lbl_info.set_use_markup(True)

            infobar_content_area = self.infobar.get_content_area()
            infobar_content_area.set_orientation(Gtk.Orientation.VERTICAL)

            infobar_content_area.pack_start(self.infobar.lbl_info, False, False, 0)
            infobar_content_area.pack_start(self.infobar.lbl, True, True, 0)

            self.content_area.pack_start(self.infobar, True, True, 0)

        else:
            self.infobar.show()
        self.wnd.show_all()

    def infobar_response(self, bar, respose_id):
        bar.hide()
