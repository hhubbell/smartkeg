#!/usr/bin/env python2
#----------------------------------------------------------------------------
# Name:         gui.py
# Purpose:      Display info from the SmartKeg database live.
# Author:       Christopher Young
# Created:      11/1/14
# Modifed:      11/13/14 [Harrison Hubbell]
#----------------------------------------------------------------------------

import gtk
import webkit
import gobject


if __name__ == '__main__':
    gobject.threads_init()
    window = gtk.Window()
    browser = webkit.WebView()
    browser.open("http://localhost")
    window.add(browser)
    window.show_all()

    gtk.main()
