#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging


class WindowGeometryPoint():
    """
    class for Main Window point setup
         window position: TOP, LEFT /
         window size: BOTTOM RIGHT
    load/save from setting in start / exit program
    """
    def __init__(self, x=400, y=200):
        self.lgr = logging.getLogger('main')

        self.__xval = 400
        self.__yval = 200

        self.x = x
        self.y = y

    def isValid_value(self, val, name):
        if not type(val) is int:
            self.lgr.debug("The param %s must be an Integer,  not '%s'",  name, type(val))
            return False

        if val < 0:
            self.lgr.debug("value for '%s' < 0", name)
            return False

        return True

    @property
    def x(self):
        return self.__xval

    @x.setter
    def x(self, val):
        if self.isValid_value(val, "pos_x"):
            self.__xval = val

    @property
    def y(self):
        return self.__yval

    @y.setter
    def y(self, val):
        if self.isValid_value(val, "pos_y"):
            self.__yval = val


class Size(WindowGeometryPoint):
    """
    child class of WindowGeometryPoint need for save/load windows size from config
    Size(width, height)
        width int  > 0
        height int > 0
    """
    def __init__(self, *args):
        WindowGeometryPoint.__init__(self, *args)

        self.WIDTH = self.x
        self.HEIGHT = self.y


class Pos(WindowGeometryPoint):
    """
    child class of WindowGeometryPoint need for save/load windows position from config
    Pos(top, left)
        top int  > 0
        left int > 0
    """
    def __init__(self, *args):
        WindowGeometryPoint.__init__(self, *args)
        self.TOP = self.x
        self.LEFT = self.y