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
import StringIO
import time
import zlib

class TCPHandler(SocketServer.StreamRequestHandler):
    def set_headers(self, fields):
        """
        @Author:        Harrison Hubbell
        @Created:       11/01/2014
        @Description:   Sets the response headers based on the fields
                        dictionary paramter
        """
        self.response_headers = 'HTTP/1.1 200 OK\r\n'

        for field in fields:
            self.response_headers += field + ': ' + fields[field] + '\r\n'

        self.response_headers += '\r\n'

    def split_headers(self, request):
        """
        @Author:        Harrison Hubbell
        @Created:       11/01/2014
        @Description:   Spits the request headers into a dictionary so 
                        header content can be easily queried.
        """
        headers = request.split('\n\n')[0]
        request_headers = {}

        for line in headers.splitlines():
            field = line.split(': ')
            if len(field) > 1:
                request_headers[field[0]] = field[1]
            else:
                request_headers['Client Request'] = field[0]

        return request_headers

    def handle(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Returns JSON to client containing supplied data.
        """
        request = self.request.recv(1024).strip()
        request_headers = self.split_headers(request)
        response_fields = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': request_headers['Accept'],
        }

        self.set_headers(response_fields)
        self.wfile.write(self.response_headers)
        self.wfile.write(self.server.response)

    def gzip(self, body):
        """
        @Author:        Harrison Hubbell
        @Created:       11/03/2014
        @Description:   Compresses response body.

        XXX: Currently not used nor working.  Responses are malformed.
        """
        output = StringIO.StringIO()
        return output.write(zlib.compressobj(body))


class TCPServer(SocketServer.TCPServer):
    def log_message(self, message):
        """
        @Author:        Harrison Hubbell
        @Created:       10/11/2014
        @Description:   Logs a message.
        """
        if self.logger: self.logger.log(message)


class ThreadedTCPServer(SocketServer.ThreadingMixIn, TCPServer):
    """Handle Requests in a Seperate Thread."""


class SocketServer(object):
    def __init__(self, host, port, pipe=None, logger=None):
        self.tcpd = ThreadedTCPServer((host, port), TCPHandler)
        self.tcpd.logger = logger
        self.update_id = 0

    def set_response(self, identifier, data):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Manages setting the TCPServer reponse.
        """
        self.tcpd.update_id = identifier
        self.tcpd.response = 'id: {}\ndata: {}\n\n'.format(identifier, data)
        
    def respond(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Handle a single request.
        """
        self.tcpd.handle()

    def main(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   Checks for updated response data and responds.
        """
        while True:
            update = self.proc_poll_recv()
            if update:
                self.update_id += 1
                self.set_response(self.update_id, update)

            self.respond()
            time.sleep(0.1)

        self.tcpd.shutdown()
