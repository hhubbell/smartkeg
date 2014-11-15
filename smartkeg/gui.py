#!/usr/bin/env python2
#----------------------------------------------------------------------------
# Name:         gui.py
# Author:       Christopher Young
# Created:      11/1/14
# Description:  Create a webkit enabled GUI to render the web interface in a
#               special purpose window.
#----------------------------------------------------------------------------

import gtk
import webkit
import gobject

if __name__ == '__main__':
    HOST = 'http://localhost'

    gobject.threads_init()
    window = gtk.Window()
    browser = webkit.WebView()
    browser.open(HOST)
    window.add(browser)
    window.show_all()

    gtk.main()
