#
# Filename:     exception.py
# Author:       Harrison Hubbell
# Date:         10/06/2015
# Description:  HTTP handlers
#

from .. import query
from . import exception
import datetime
import json
import urllib

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
            raise exception.APINotConnectedError

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
                raise exception.APIMalformedError(endpoint, params=params)

        else:
            raise exception.APIMalformedError(endpoint, params=params)

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
            raise exception.APIMalformedError(endpoint)

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
                raise exception.APIForbiddenError(url, method=method)
        else:
            raise exception.APIMalformedError(url, method=method)

        return json.dumps(
            res,
            default=lambda x: str(x) if isinstance(x, datetime.date) else x
        )
