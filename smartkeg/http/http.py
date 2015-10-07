#
# Filename:     http_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
#

from socketserver import ThreadingMixIn
from multiprocessing import Process, Lock
from . import exception, handler
import logging
import http.server
import io
import socket
import qrcode
import qrcode.image.svg
import urllib.parse
import gzip

class RequestHandler(http.server.BaseHTTPRequestHandler):
    _INDEX = 'index.html'    

    def get_content_type(self, req):
        """ 
        @author:        Harrison Hubbell
        @created:       09/01/2014
        @description:   Return content type based on file.  Essentially
                        just a lot of if statements
        """
        if req.endswith('.css'):    return 'text/css'
        if req.endswith('.html'):   return 'text/html'
        if req.endswith('.ico'):    return 'image/x-icon'
        if req.endswith('.js'):     return 'application/javascript'
        if req.endswith('.pdf'):    return 'application/pdf'
        if req.endswith('.png'):    return 'image/png'
        if req.endswith('.svg'):    return 'image/svg+xml'

    def get_resource(self):
        """
        @author:        Harrison Hubbell
        @created:       10/05/2014
        @description:   Locates the requested resource.
        """
        page_buffer = None
        content_type = None

        if self.path[1:4] == 'api':
            page_buffer, content_type = self.server.api.handle(
                self.command,
                self.path[5:],
                self.headers,
                self.rfile
            )

        elif self.path[1:4] == 'sse':
            page_buffer, content_type = self.server.sse.handle()

        else:
            page = self.path[1:] or self._INDEX
            content_type = self.get_content_type(page)

            with open(self.server.root + page, 'rb') as f:
                page_buffer = f.read()

        return page_buffer, content_type

    def encode(self, stream):
        """
        @author:        Harrison Hubbell
        @created:       04/06/2015
        @description:   Compresses response body.
        """
        ENCODING = 'gzip'
        output = io.BytesIO()
        encoding = None
        fbuffer = stream

        if ENCODING in self.headers['Accept-Encoding'] and stream is not None:
            with gzip.GzipFile(fileobj=output, mode='w', compresslevel=5) as f:
                f.write(stream)
            
            encoding = ENCODING
            fbuffer = output.getvalue()              

        return fbuffer, encoding

    def log_message(self, format, *args):
        """
        @author:        Harrison Hubbell
        @created:       09/01/2014
        @description:   Overrides standard logging functionality to
                        log server actions to a file.
        """
        logging.debug(args)

    def do_GET(self):
        """
        @author:        Harrison Hubbell
        @created:       09/01/2014
        @description:   Handles GET requests
        """
        try:
            data, content_type = self.get_resource()
            data, content_encoding = self.encode(data)

            self.send_response(200)
            self.send_header("Content-type", content_type)
            if content_encoding:
                self.send_header("Content-encoding", content_encoding)
            self.end_headers()
            self.wfile.write(data)

        except IOError as e:
            self.send_error(404)
            logging.info(e)

        except excepiton.APINotConnectedError as e:
            self.send_error(503)
            logging.error(e)

        except excepiton.APIMalformedError as e:
            self.send_error(400)
            logging.info(e)

        except excepiton.APIForbiddenError as e:
            self.send_error(403)
            logging.info(e)

        except Exception as e:
            self.send_error(500)
            logging.critical('{} {} caused an Internal Server Error'.format(
                self.command,
                self.path
            ))
            logging.critical(e)  

    def do_POST(self):
        """
        @author:        Harrison Hubbell
        @created:       11/21/2014
        @description:   Handles POST requests
        """
        try:
            data, content_type = self.get_resource()
            data, content_encoding = self.encode(data)

            self.send_response(200)
            self.send_header("Content-type", content_type)
            if content_encoding:
                self.send_header("Content-encoding", content_encoding)
            self.end_headers()
            self.wfile.write(data)

        except IOError as e:
            self.send_error(404)
            logging.info(e)

        except excepiton.APINotConnectedError as e:
            self.send_error(503)
            logging.error(e)

        except excepiton.APIMalformedError as e:
            self.send_error(400)
            logging.info(e)

        except excepiton.APIForbiddenError as e:
            self.send_error(403)
            logging.info(e)

        except Exception as e:
            self.send_error(500)
            logging.critical('{} {} caused an Internal Server Error'.format(
                self.command,
                self.path
            ))
            logging.critical(e)

    
class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """Handle Requests in a Seperate Thread."""
    def __init__(self, addr, handler, api, sse, root):
        super(ThreadedHTTPServer, self).__init__(addr, handler)
        self.api = api
        self.sse = sse
        self.root = root


class HTTPServerManager(object):
    def __init__(self, host, port, path, dbi=None):
        self.host = host
        self.port = port
        self.path = path
        self.dbi = dbi
        self.update_id = 0
        self.lock = Lock();        
        self.create_qrcode()

    def create_qrcode(self):
        """
        @author:        Harrison Hubbell
        @created:       11/18/2014
        @description:   Gets the current interface address of the server,
                        and renders a QR Code that allows devices to go 
                        to that address.
        """
        GOOGLE = ('8.8.8.8', 80)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(GOOGLE)
        address = 'http://' + sock.getsockname()[0]
        sock.close()
 
        factory = qrcode.image.svg.SvgPathImage
        factory.QR_PATH_STYLE = 'fill:#C0392B;fill-opacity:1;fill-rule:nonzero;stroke:none'

        qr = qrcode.QRCode(version=1, box_size=10, border=0)
        qr.image_factory = factory
        qr.add_data(address)
        qr.make()

        image = qr.make_image()
        image.save(self.path + 'static/img/qrcode.svg')

    def sse_response(self, data):
        """
        @author:        Harrison Hubbell
        @created:       04/06/2015
        @description:   Manages setting the HTTPServer sse reponse.
        """
        self.lock.acquire()
        
        with open(self.path + '/static/sse.txt', 'w') as f:
            self.update_id += 1
            f.write('id: {}\ndata: {}\n\n'.format(self.update_id, data))
            
        self.lock.release()
            
    def spawn_server(self, host=None, port=None):
        """
        @author:        Harrison Hubbell
        @created:       04/13/2015
        @description:   Spawn the http server instance.
        """
        host = host if host is not None else self.host
        port = port if port is not None else self.port
        
        self.httpd = ThreadedHTTPServer(
            (host, port),
            RequestHandler,
            handler.APIHandler(self.dbi),
            handler.SSEHandler(self.path + '/static/sse.txt', self.lock),
            self.path
        )
        
        self.httpd.serve_forever()

    def start(self):
        """
        @author:        Harrison Hubbell
        @created:       04/13/2015
        @description:   Spawn a thread and a shared memory pool for
                        setting new SSE responses.
        """
        Process(target=self.spawn_server).start()
