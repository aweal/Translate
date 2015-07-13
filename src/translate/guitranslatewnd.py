#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Pango

import logging
import os

ICO_APP_SVG = "/usr/share/icons/hicolor/scalable/apps/translate.svg"


class MainWnd(Gtk.ApplicationWindow):
    def __init__(self, app, *args, **kwargs):
        super().__init__(title="Translate", application=app, *args, **kwargs)
        self.app = app
        Gtk.Window.__init__(self, title="Translate", application=app)
        self.lgr = logging.getLogger('mainwnd')
        # self.set_icon_from_file(os.path.dirname(__file__) + "/resource/ico.png")
        # self.set_icon_name('translate')
        self.def_ico = self.get_icon()
        if self.def_ico:
            self.set_default_icon(self.def_ico)

        self.set_keep_above(True)
        self._cb_primary_state = False
        self._cb_selection_state = False
        self.__single_mode = True
        self.clipboard_primary = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        self.clipboard_primary.connect('owner-change', self.on_cb_primary_change)
        self.clipboard_selection = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clipboard_selection.connect('owner-change', self.on_cb_selection_change)
        grid = Gtk.Grid()
        self.add(grid)
        self.switch = Gtk.Switch()
        self.switch.set_valign(Gtk.Align.START)
        self.switch.set_halign(Gtk.Align.CENTER)
        self.switch.connect("notify::active", self.on_switch_change)
        grid.attach(self.switch, 2, 0, 2, 1)
        self.lbl_primary = Gtk.Label()
        scroll_wnd_primary = self.create_notselectable_widget(self.lbl_primary, True)
        grid.attach(scroll_wnd_primary, 0, 1, 3, 2)
        self.lbl_selection = Gtk.Label()
        scroll_wnd_selection = self.create_notselectable_widget(self.lbl_selection, True)
        grid.attach(scroll_wnd_selection, 3, 1, 3, 2)
        self.pb = Gtk.ProgressBar()
        self.pb.set_pulse_step(0.5)
        self.pb.set_visible(False)
        grid.attach(self.pb, 0, 3, 6, 1)
        self.lbl_trans_primary = Gtk.Label()
        scroll_wnd_primary_transl = self.create_notselectable_widget(self.lbl_trans_primary, True)
        grid.attach(scroll_wnd_primary_transl, 0, 4, 3, 1)
        self.lbl_trans_selection = Gtk.Label("")
        scroll_wnd_selection_transl = self.create_notselectable_widget(self.lbl_trans_selection, True)
        grid.attach(scroll_wnd_selection_transl, 3, 4, 3, 1)
        self.primary_cp_widgets = (scroll_wnd_primary, scroll_wnd_primary_transl)
        self.selection_cp_widgets = (scroll_wnd_selection, scroll_wnd_selection_transl)

    def create_notselectable_widget(self, widget, scrolled=False):
        if type(widget) is Gtk.Label:
            widget.connect("focus-in-event", self.label_focus_in)
            widget.connect("focus-out-event", self.label_focus_out)

            widget.set_margin_left(10)
            widget.set_margin_right(10)
            widget.set_selectable(True)

            widget.set_hexpand(True)

            widget.set_line_wrap(True)
            widget.set_line_wrap_mode(Pango.WrapMode.WORD)

            widget.set_valign(Gtk.Align.START)
            widget.set_halign(Gtk.Align.START)

            if scrolled:
                scroll_wnd = Gtk.ScrolledWindow()
                scroll_wnd.add_with_viewport(widget)
                scroll_wnd.set_vexpand(True)
                scroll_wnd.set_hexpand(True)

                widget = scroll_wnd

        return widget

    def get_icon(self):
        if os.path.exists(os.path.dirname(__file__) + "/resource/"):
            return GdkPixbuf.Pixbuf.new_from_file(os.path.dirname(__file__) + "/resource/ico.png")

        if os.path.exists(os.path.dirname(ICO_APP_SVG)):
            return GdkPixbuf.Pixbuf.new_from_file(ICO_APP_SVG)

        return None

    def switch_visible_controls(self, enable=False):
        if enable:
            status_primary = True
            status_selection = True
        else:
            status_primary = not self.switch.get_active()
            status_selection = not status_primary

        for widget in self.primary_cp_widgets:
            widget.set_visible(status_primary)

        for widget in self.selection_cp_widgets:
            widget.set_visible(status_selection)

    def on_switch_change(self, switch, *args):
        # hint! clipboard_primary_status enable / disable in label_focus_*
        # hint!! switch_visible_controls in single_mode
        status = switch.get_active()
        self.clipboard_primary_status = not status

        if self.single_mode:
            self.clipboard_selection_status = status
            self.switch_visible_controls()

            if status:
                self.primary_text = ''
                self.translated_primary_text = ''
            else:
                self.selection_text = ''
                self.translated_selection_text = ''

    @property
    def clipboard_primary_status(self):
        return self._cb_primary_state

    @clipboard_primary_status.setter
    def clipboard_primary_status(self, status):
        self.lgr.debug('clipboard primary is: %s', status)
        self._cb_primary_state = status

        if status:
            self.on_cb_primary_change(self.clipboard_primary, None)
        else:
            self.pb.set_visible(False)
            self.app.timer_stop()

    @property
    def clipboard_selection_status(self):
        return self._cb_selection_state

    @clipboard_selection_status.setter
    def clipboard_selection_status(self, status):
        self.lgr.debug('clipboard selection is: %s', status)

        type_status = type(status)
        if type_status is not bool:
            self.lgr.error('Wrong type of status `%s`, Boolean required!', type_status)
        else:
            self._cb_selection_state = status

            if status:
                self.on_cb_selection_change(self.clipboard_selection, None)

    # controls may changed in future ;)
    @property
    def primary_text(self):
        return self.lbl_primary.get_text()

    @primary_text.setter
    def primary_text(self, text):
        if text is not None:
            self.lbl_primary.set_text(str(text))

    @property
    def selection_text(self):
        return self.lbl_selection.get_text()

    @selection_text.setter
    def selection_text(self, text):
        if text is not None:
            self.lbl_selection.set_text(str(text))

    @property
    def translated_primary_text(self):
        return self.lbl_trans_primary.get_text()

    @translated_primary_text.setter
    def translated_primary_text(self, text):
        self.lbl_trans_primary.set_text(str(text))

    @property
    def translated_selection_text(self):
        return self.lbl_trans_selection.get_text()

    @translated_selection_text.setter
    def translated_selection_text(self, text):
        if text is not None:
            self.lbl_trans_selection.set_text(str(text))

    # view:
    @property
    def single_mode(self):
        return self.__single_mode

    @single_mode.setter
    def single_mode(self, setup_mode):
        """
        setter single_mode:
            :param setup_mode: Boolean enable / disable single mode view
        """
        self.__single_mode = setup_mode

        if setup_mode:
            self.switch_visible_controls()
        else:
            self.lgr.debug('Enable all controls: ')
            self.switch_visible_controls(True)
            self.clipboard_primary_status = not self.switch.get_active()
            self.clipboard_selection_status = True

    def label_focus_in(self, lbl, selection_data):
        """
        When you select text labels clipboards does not work
        """
        if not self.switch.get_active():
            self.clipboard_primary_status = False

    def label_focus_out(self, lbl, selection_data):
        if not self.switch.get_active():
            self.clipboard_primary_status = True

    def translate_primary_text(self):
        self.app.timer_start()
        self.pb.set_visible(True)

    def translate_selection_text(self):
        if self.selection_text is None:
            self.lgr.debug('Selection text is None')
            return False
        transl = self.app.translate(self.selection_text)
        if transl is not None:
            self.translated_selection_text = transl

    # clipboard:
    # bicycle #3   frieze on clipboard.wait_for_text()
    def check_cp_text(self, txt, old_text):
        if txt is None:
            # self.lgr.debug('The clipboard is empty')
            return False

        if len(txt) < 2:
            # self.lgr.debug('The text is too short ...')
            return False

        if old_text == txt:
            # self.lgr.debug('Skip the same text for translation')
            return False

        return txt

    def _request_primary_text(self, clipboard, text):
        if self.check_cp_text(text, self.primary_text):
            self.primary_text = text
            self.translate_primary_text()

    def _request_selection_text(self, clipboard, text):
        if self.check_cp_text(text, self.selection_text):
            self.selection_text = text
            self.translate_selection_text()

    def on_cb_primary_change(self, clipboard, *args):
        if not self.clipboard_primary_status:
            return False

        self.pb.pulse()
        clipboard.request_text(self._request_primary_text)

    def on_cb_selection_change(self, clipboard, *args):
        if not self.clipboard_selection_status:
            return False
        clipboard.request_text(self._request_selection_text)

    # actions:
    def act_about_execute(self, action, parameter):
        about_wnd = Gtk.AboutDialog(parent=self)
        # about_wnd.set_icon_from_file(os.path.dirname(__file__) + "/resource/ico.png")

        authors = ["Aweal"]
        # about_wnd.set_logo(GdkPixbuf.Pixbuf.new_from_file(os.path.dirname(__file__) + "/resource/logo.png"))
        if self.def_ico:
            about_wnd.set_logo(GdkPixbuf.Pixbuf.new_from_file(ICO_APP_SVG))
            about_wnd.set_default_icon(self.def_ico)

        # about_wnd.set_logo_icon_name('translate')
        about_wnd.set_program_name("Translate")
        about_wnd.set_copyright(
            "Copyright \xa9 2015 Aweal")
        about_wnd.set_authors(authors)

        about_wnd.set_website("http://github.com/aweal/translate")
        about_wnd.set_website_label("show source on github")

        about_wnd.connect("response", self.on_close)
        about_wnd.show()

    def on_close(self, widget, resp):
        widget.destroy()
