#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging

from gi.repository import Gdk
from gi.repository import GLib

import threading
import time


class Timer(threading.Thread):
    def __init__(self, call_back, pulse_cb=None, count=5):
        threading.Thread.__init__(self)
        self.lgr = logging.getLogger('timer')

        self.daemon = True
        self.call_back = call_back
        self._wait_time = count
        self._count = count
        self.event_do_exit = threading.Event()
        self.pulse_cb = pulse_cb

        # self.work: sett / gett if enable
        self._work = False

    def get_status(self):
        return self.isAlive()

    @property
    def work(self):
        return self._work

    @work.setter
    def work(self, enable):
        self._work = enable

        if enable:
            self._count = self._wait_time
        else:
            self._count = 0

    def tick_callback(self):
        if self.work:
            Gdk.threads_enter()
            GLib.idle_add(self.pulse_cb)
            Gdk.threads_leave()

    def timer_end(self):
        if self.work:
            Gdk.threads_enter()
            GLib.idle_add(self.call_back)
            Gdk.threads_leave()
            self.work = False

    def run(self):
        while not self.event_do_exit.isSet():
            # print('.', end="", flush=True)
            if self.work:
                if self._count > 0:
                    self._count -= 1
                    self.tick_callback()

                if self._count == 0:
                    self.timer_end()
            time.sleep(1)

    def halt(self):
        self.lgr.debug('Halt!')
        self.event_do_exit.set()
