#
# Filename:     exception.py
# Author:       Harrison Hubbell
# Date:         10/06/2015
# Description:  HTTP module exceptions
#

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
