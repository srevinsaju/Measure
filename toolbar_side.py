# -*- coding: utf-8 -*-
#! /usr/bin/python
#
# Author:  Arjun Sarwal   arjun@laptop.org
# Copyright (C) 2007, Arjun Sarwal
# Copyright (C) 2009-11 Walter Bender
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA


import gtk
from gettext import gettext as _

from sugar.graphics.toolbutton import ToolButton


class SideToolbar(gtk.Toolbar):
    """ A toolbar on the side of the canvas for adjusting gain/bias """

    LOWER = 0.0
    UPPER = 4.0

    def __init__(self, activity, channel=0):
        """ Set up initial toolbars """
        gtk.Toolbar.__init__(self)

        self.activity = activity
        self._channel = channel
        if self._channel == 0:
            self.show_toolbar = True
        else:  # Don't show second channel until we need it
            self.show_toolbar = False
        self.mode = 'sound'
        self.mode_values = {'sound': 3, 'sensor': 2}

        self._invert = ToolButton('invert')
        self._invert.set_tooltip(_('Invert'))
        self._invert.connect('clicked', self._invert_control_cb)
        self._invert.show()
        self.activity.wave.set_invert_state(False, channel=self._channel)

        self.button_up = ToolButton('amp-high')
        self.button_up.set_tooltip(_('Increase amplitude'))
        self.button_up.connect('clicked', self._button_up_cb)
        self.button_up.show()

        self.adjustmenty = gtk.Adjustment(self.mode_values[self.mode],
                                          self.LOWER, self.UPPER,
                                          0.1, 0.1, 0.0)
        self.adjustmenty.connect('value_changed', self._yscrollbar_cb,
                                 self.adjustmenty)
        self.yscrollbar = gtk.VScale(self.adjustmenty)
        self.yscrollbar.set_draw_value(False)
        self.yscrollbar.set_inverted(True)
        self.yscrollbar.set_update_policy(gtk.UPDATE_CONTINUOUS)

        self.button_down = ToolButton('amp-low')
        self.button_down.set_tooltip(_('Decrease amplitude'))
        self.button_down.connect('clicked', self._button_down_cb)
        self.button_down.show()

        self.box1 = gtk.VBox(False, 0)
        if self._channel == 0:
            self.box1.pack_start(self._color_wave(self.activity.stroke_color),
                                 False, True, 0)
        elif self._channel == 1:
            self.box1.pack_start(self._color_wave(self.activity.fill_color),
                                 False, True, 0)
        else:
            self.box1.pack_start(self._color_wave('#FFFFFF'), False, True, 0)
        self.box1.pack_start(self._invert, False, True, 0)
        self.box1.pack_start(self.button_up, False, True, 0)
        self.box1.pack_start(self.yscrollbar, True, True, 0)
        self.box1.pack_start(self.button_down, False, True, 0)

        self.set_show_hide(False)

    def _yscrollbar_cb(self, adjy, data=None):
        """ Callback for scrollbar """
        if self.mode == 'sound':
            self.activity.wave.set_mag_params(1.0, adjy.value,
                                              channel=self._channel)
            # self.activity.audiograb.set_capture_gain(
            #     adjy.value * 100 / (self.UPPER - self.LOWER))
            self.activity.wave.set_bias_param(0,
                                              channel=self._channel)
        elif self.mode == 'sensor':
            self.activity.wave.set_bias_param(int(
                    300 * (adjy.value - (self.UPPER - self.LOWER) / 2.)),
                                              channel=self._channel)
        self.mode_values[self.mode] = adjy.value
        return True

    def _button_up_cb(self, data=None):
        """Moves slider up"""
        new_value = self.yscrollbar.get_value() + (self.UPPER - self.LOWER) \
            / 100.
        if new_value <= self.UPPER:
            self.yscrollbar.set_value(new_value)
        else:
            self.yscrollbar.set_value(self.UPPER)
        return True

    def _button_down_cb(self, data=None):
        """Moves slider down"""
        new_value = self.yscrollbar.get_value() - (self.UPPER - self.LOWER) \
            / 100.
        if new_value >= self.LOWER:
            self.yscrollbar.set_value(new_value)
        else:
            self.yscrollbar.set_value(self.LOWER)
        return True

    def set_show_hide(self, show=True, mode='sound'):
        """ Show or hide the toolbar """
        self.show_toolbar = show
        self.set_mode(mode)

    def set_mode(self, mode='sound'):
        """ Set the toolbar to either 'sound' or 'sensor' """
        self.mode = mode
        if self.mode == 'sound':
            self.button_up.set_icon('amp-high')
            self.button_up.set_tooltip(_('Increase amplitude'))
            self.button_down.set_icon('amp-low')
            self.button_down.set_tooltip(_('Decrease amplitude'))
        elif self.mode == 'sensor':
            self.button_up.set_icon('bias-high')
            self.button_up.set_tooltip(_('Increase bias'))
            self.button_down.set_icon('bias-low')
            self.button_down.set_tooltip(_('Decrease bias'))
            self._invert.show()
        self.yscrollbar.set_value(self.mode_values[self.mode])
        return

    def _invert_control_cb(self, data=None):
        """ Callback for Invert Button """
        if self.activity.wave.get_invert_state(channel=self._channel):
            self.activity.wave.set_invert_state(False, self._channel)
            self._invert.set_icon('invert')
            self._invert.show()
        else:
            self.activity.wave.set_invert_state(True, self._channel)
            self._invert.set_icon('invert2')
            self._invert.show()
        # self._update_string_for_textbox()  # from sound_toolbar
        return False

    def _color_wave(self, color):
        svg = '<?xml version="1.0" ?>\n\
<!DOCTYPE svg  PUBLIC "-//W3C//DTD SVG 1.1//EN"  \n\
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n\
<svg enable-background="new 0 0 55.125 55" height="55px" version="1.1" \n\
viewBox="0 0 55.125 55" width="55.125px" x="0px" xml:space="preserve" \n\
xmlns="http://www.w3.org/2000/svg" \n\
xmlns:xlink="http://www.w3.org/1999/xlink" y="0px">\n\
<path d="M9.066,27.5 c2.32-6.917,4.666-13.834,9.255-13.834\n\
c9.179,0,9.179,27.668,18.358,27.668c4.59,0,6.986-6.917,9.332-13.834" \n\
fill="none" stroke="%s" stroke-linecap="round" stroke-width="3.5"/>\n\
</svg>' % (color)
        pixbuf = svg_str_to_pixbuf(svg)
        img = gtk.Image()
        img.set_from_pixbuf(pixbuf)
        img_tool = gtk.ToolItem()
        img_tool.add(img)
        return img_tool


def svg_str_to_pixbuf(svg_string):
    ''' Load pixbuf from SVG string '''
    pl = gtk.gdk.PixbufLoader('svg')
    pl.write(svg_string)
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf
