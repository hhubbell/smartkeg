#
# Filename:     http_server.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Is responsible for serving data over HTTP
#

from socketserver import ThreadingMixIn
from multiprocessing import Process, Lock
from . import query
import logging
import http.server
import io
import socket
import qrcode
import qrcode.image.svg
import json
import urllib.parse
import gzip
import datetime

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

        except APINotConnectedError as e:
            self.send_error(503)
            logging.error(e)

        except APIMalformedError as e:
            self.send_error(400)
            logging.info(e)

        except APIForbiddenError as e:
            self.send_error(403)
            logging.info(e)

        except Exception as e:
            self.send_error(500)
            logging.critical('{} {} caused an Internal Server Error'.format(self.command, self.path))
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

        except APINotConnectedError as e:
            self.send_error(503)
            logging.error(e)

        except APIMalformedError as e:
            self.send_error(400)
            logging.info(e)

        except APIForbiddenError as e:
            self.send_error(403)
            logging.info(e)

        except Exception as e:
            self.send_error(500)
            logging.critical('{} {} caused an Internal Server Error'.format(self.command, self.path))
            logging.critical(e)

class SSEHandler(object):
    CONTENT_TYPE = 'text/event-stream'
    
    def __init__(self, filename, lock):
        self.filename = filename
        self.lock = lock

    def __str__(self):
        self.lock.aquire()

        with open(self.filename, 'r') as f:
            data = f.read()

        self.lock.release()

        return data

    def __bytes__(self):
        self.lock.acquire()

        with open(self.filename, 'rb') as f:
            data = f.read()

        self.lock.release()

        return data

    def handle(self, byte=True):
        return bytes(self) if byte else str(self), self.CONTENT_TYPE


class APIHandler(object):
    CONTENT_TYPE = 'text/plain'

    def __init__(self, dbi):
        self.dbi = dbi

    def check(self):
        if not self.dbi:
            raise APINotConnectedError

    def handle(self, method, url, headers, rfile, byte=True):
        self.check()
        page_buffer = self.transact(method, url, headers, rfile)
        page_buffer = page_buffer.encode('utf-8') if byte else page_buffer
        
        return page_buffer, self.CONTENT_TYPE

    def parse_url(self, method, url, headers, rfile):
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.split('/')

        if method == 'GET':
            params = urllib.parse.parse_qsl(parsed.query)
        elif method == 'POST':
            length = int(headers.getheader('Content-Length'))
            params = urllib.parse.parse_qsl(rfile.read(length))

        return path, params

    def get(self, endpoint, params):
        sql = None
        
        if endpoint == 'beer': 
            sql = query.get_beers(params)

        elif endpoint == 'brewer':
            sql = query.get_brewers(params)

        elif endpoint == 'serving':
            sql = query.get_now_serving()

        elif endpoint == 'daily':
            sql = query.get_daily()

        elif endpoint == 'remaining':
            fmt = next((x[1] for x in params if x[0] == 'format'), 'percent')
                    
            if fmt == 'percent':
                sql = query.get_percent_remaining()

            elif fmt == 'volume':
                sql = query.get_volume_remaining()
                
            else:
                raise APIMalformedError(endpoint, params=params)
        
        else:
            raise APIMalformedError(endpoint, params=params)

        with self.dbi as dbi:
            return dbi.select(*sql) if sql else None

    def set(self, endpoint, params):
        res = None
        
        if endpoint == 'keg':
            if 'replace' in params:
                with self.dbi as dbi:
                dbi.update(*query.rem_keg(params['replace']))        
                res = dbi.insert(*query.set_keg(params))
                
        elif endpoint == 'rating':
            with self.dbi as dbi:
                res = dbi.insert(*query.set_rating(params))

        else:
            raise APIMalformedError(endpoint)
        
        return res

    def transact(self, method, url, headers, rfile):
        """
        @author:        Harrison Hubbell
        @created:       12/14/2014
        @description:   Handle user requests that require database
                        interaction.  get's should be method agnostic,
                        while set's should require a POST.
        """
        res = None
        
        path, params = self.parse_url(method, url, headers, rfile)

        if len(path) >= 2:
            if path[0] == 'get':
                res = self.get(path[1], params)
                        
            elif path[0] == 'set' and method == 'POST':
                res = self.set(path[1], params)
                
            else:
                raise APIForbiddenError(url, method=method)
        else:
            raise APIMalformedError(url, method=method)

        return json.dumps(res, default=lambda x: str(x) if isinstance(x, datetime.date) else x)


class APINotConnectedError(Exception):
    def __str__(self):
        return 'API has no database connection'


class APIMalformedError(Exception):
    ERRORSTRING = 'API Query "{:5}{}{}" is malformed'
    def __init__(self, url, params=None, method=None):
        self.params = '?' + urllib.parse.urlencode(params) if params else ''
        self.method = method or ''
        self.url = url

    def __str__(self):
        return self.ERRORSTRING.format(self.method, self.url, self.params)


class APIForbiddenError(APIMalformedError):
    ERRORSTRING = 'API Query "{:5}{}{}" is forbidden'

    
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
            APIHandler(self.dbi),
            SSEHandler(self.path + '/static/sse.txt', self.lock),
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
