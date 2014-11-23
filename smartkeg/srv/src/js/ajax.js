/* ------------------------------------------------------------------------ *
 * Filename:    ajax.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: Manage asyncronous calls to a server.
 * Requires:    socket.js
 * ------------------------------------------------------------------------ */

function Ajax(host) {
    this.xmlhttp = new XMLHttpRequest();
    this.host = host;
}

Ajax.prototype.send = function(method, payload) {
    var self = this;
    
    return new Promise(function(resolve, reject) {
        self.xmlhttp.open(method, self.host, true);
        self.xmlhttp.onload = function() {
            if (self.xmlhttp.status == 200) {
                resolve(self.xmlhttp.response);
            } else {
                reject(Error(self.xmlhttp.statusText));
            }
        };

        self.xmlhttp.onerror = function() {
            reject(Error('Network Error'));
        }

        self.xmlhttp.send(payload);
    });
}
