# ----------------------------------------------------------------------------
# Filename:     http_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
# ----------------------------------------------------------------------------

from ConfigParser import ConfigParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from logger import SmartkegLogger
import json

class RequestHandler(BaseHTTPRequestHandler):
    HTTP_OK             = 200
    HTTP_PAGE_NOT_FOUND = 404
    SERVER_DIR = 'srv/'
    INDEX = 'index.html'
    _CONFIG_PATH = 'etc/config.cfg'

    def get_content_type(self, req):
        """ 
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Return content type based on file.  Essentially 
                        just a lot of if statements
        """
        if req.endswith('.css'):    return 'text/css'        
        if req.endswith('.html'):   return 'text/html'
        if req.endswith('.ico'):    return 'image/x-icon'
        if req.endswith('.js'):     return 'application/javascript'
        if req.endswith('.pdf'):    return 'application/pdf'
        if req.endswith('.png'):    return 'image/png'

    def get_page(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Locates the requested page.
        """
        if self.path[1:] is '': 
            page = self.SERVER_DIR + self.INDEX
        else:
            page = self.SERVER_DIR + self.path[1:]

        return page

    def log_message(self, format, *args):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Overrides standard logging functionality to
                        log server actions to a file.
        """
        logger = SmartkegLogger(self._CONFIG_PATH)
        logger.log(['[HTTP Server]', args])

    # --------------------
    # BUILTIN HTTP METHODS
    # --------------------
    def do_GET(self):
        page = self.get_page()
        content_type = self.get_content_type(page)

        with open(page) as p:
            self.send_response(self.HTTP_OK)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(p.read())

    def do_POST(self):
        #POST Stuff
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle Requests in a Seperate Thread."""
    

class SmartkegHTTPServer:    
    def __init__(self, host, port):
        self.httpd = ThreadedHTTPServer((host, port), RequestHandler)
        
    def main(self):
        self.httpd.serve_forever()

if __name__ == '__main__':
    _CONFIG_PATH = 'etc/config.cfg'
    _HEADER = 'SmartkegHTTPServer'

    cfg = ConfigParser()
    cfg.read(_CONFIG_PATH)
    host = cfg.get(_HEADER, 'host')
    port = cfg.getint(_HEADER, 'port')
        
    server = SmartkegHTTPServer(host, port)
    server.main()
