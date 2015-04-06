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
import gzip

class ResponseHeader(object):
    def __init__(self, code):
        self.fields = {}
        self.code = code

    def __str__(self):
        rep = self.code + '\r\n'
        for field in self.fields:
            rep += field + ': ' + self.fields[field] + '\r\n'

        return rep + '\r\n'
        

    def add(self, key, value):
        self.fields[str(key)] = str(value)

class TCPHandler(SocketServer.StreamRequestHandler):
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
        ENCODE_AS = 'gzip'

        request = self.request.recv(1024).strip()        
        response = self.server.response

        self.request_header = self.split_headers(request)
        self.response_header = ResponseHeader('HTTP/1.1 200 OK')        

        self.response_header.add('Access-Control-Allow-Origin', '*')
        self.response_header.add('Content-Type', self.request_header['Accept'])

        if ENCODE_AS in self.request_header['Accept-Encoding']:
            response = self.encode(response)

        self.wfile.write(str(self.response_header))
        self.wfile.write(response)

    def encode(self, body):
        """
        @Author:        Harrison Hubbell
        @Created:       04/06/2015
        @Description:   Compresses response body.
        """
        output = StringIO.StringIO()
        
        self.response_header.add('Content-encoding', 'gzip')

        with gzip.GzipFile(fileobj=output, mode='w', compresslevel=5) as f:
            f.write(body)

        return output.getvalue()


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
        self.tcpd.handle_request()

    def serve_forever(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   Checks for updated response data and responds.
        """
        while True:
            #update = self.proc_poll_recv()
            #if update:
            #    self.update_id += 1
            #    self.set_response(self.update_id, update)

            self.respond()
            time.sleep(0.1)

        self.tcpd.shutdown()
