# ----------------------------------------------------------------------------
# Filename:     socket_server.py
# Author:       Harrison Hubbell
# Date:         10/07/2014
# Description:  Is responsible for serving data over socket interface to other
#               processes that need data, as well as 3rd party clients such as 
#               asyncronous javascript calls from the client web browser or 
#               some API; for the latter reason, the socket specified will 
#               allow connections from any origin.
# ----------------------------------------------------------------------------

import SocketServer
from logger import SmartkegLogger

class TCPHandler(SocketServer.StreamRequestHandler):
    _BASE_DIR = '/usr/local/src/smartkeg/'
    _CONFIG_PATH = _BASE_DIR + 'etc/config.cfg'
    
    def log_message(self, message):
        """
        @Author:        Harrison Hubbell
        @Created:       10/11/2014
        @Description:   Logs a message.
        """
        logger = SmartkegLogger(self._CONFIG_PATH)
        logger.log(message)
    
    def send_headers(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Sends headers to the requester.
        """
        self.wfile.write(
            "HTTP/1.1 200 OK\r\n" \
            "Access-Control-Allow-Origin: *\r\n" \
            "Content-Type: text/plain\r\n\r\n"
        )        

    def handle(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Returns JSON to client containing supplied data.
        """
        self.send_headers()
        self.wfile.write(self.server.response)
        self.log_message(['[Socket Server]', 'Request from', self.client_address[0]])


class TCPServer(SocketServer.TCPServer):
    def set_response(self, response):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Allows other Python objects to set the default
                        response date of the handler.
        """
        self.response = response


class ThreadedTCPServer(SocketServer.ThreadingMixIn, TCPServer):
    """Handle Requests in a Seperate Thread."""


class SmartkegSocketServer:
    def __init__(self, host, port):
        self.tcpd = ThreadedTCPServer((host, port), TCPHandler)

    def set_response(self, response):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Abstracts the TCPServer set_response out a bit
                        further to add the ability for any object using
                        SmartkegSocketServer to set the response.
        """
        self.tcpd.set_response(response)
        
    def respond(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Handle a single request.
        """
        self.tcpd.handle_request()
