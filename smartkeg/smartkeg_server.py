# ----------------------------------------------------------------------------
# Filename:     smartkeg_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
# ----------------------------------------------------------------------------

from multiprocessing import Pipe
import BaseHTTPServer
import json

class Request_Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    HTTP_OK             = 200
    HTTP_PAGE_NOT_FOUND = 404
    SERVER_DIR = 'srv/'
    INDEX = 'index.html'
    LOG_DIR = 'etc/log/'
    LOG_FILE = 'smartkeg_server.log'

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

    def log(self, message=None):
        log = self.LOG_DIR + self.LOG_FILE

        with open(log, 'w') as l:
            if not message:
                message = (
                    self.client_address[0] + ' [' +
                    self.date_time_string() + '] ' +
                    self.protocol_version + ' ' + 
                    self.command + ' ' + 
                    self.path
                )

            l.write(message + '\n')
        l.close()

    # --------------------
    # BUILTIN HTTP METHODS
    # --------------------
    def do_GET(self):
        if self.path[1:] == '': 
            page = self.SERVER_DIR + self.INDEX
        else:
            page = self.SERVER_DIR + self.path[1:]

        content_type = self.get_content_type(page)

        self.log()        
        with open(page) as p:
            self.send_response(self.HTTP_OK)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(p.read())

    def do_POST(self):
        #POST Stuff
        return
    

class Smartkeg_Server:    
    def __init__(self, pipe, host, port):
        self.httpd = BaseHTTPServer.HTTPServer((host, port), Request_Handler)
        
    def main(self):
        self.httpd.serve_forever()
