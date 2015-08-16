#!/usr/bin/env python2
#--------------------------------------------------------------------------
# Name:         gui.py
# Author:       Christopher Young
# Created:      11/1/14
# Description:  Create a webkit enabled GUI to render the web interface in 
#               a special purpose window.  Render the host provided as the 
#               first if applicable, otherwise render localhost.
#--------------------------------------------------------------------------

import sys
import gtk
import webkit
import gobject

DEFAULT_HOST = 'http://localhost'

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST

    gobject.threads_init()
    window = gtk.Window()
    browser = webkit.WebView()
    browser.open(host)
    window.add(browser)
    window.show_all()

    gtk.main()
