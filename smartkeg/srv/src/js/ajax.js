/* ------------------------------------------------------------------------ *
 * Filename:    ajax.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: Manage asyncronous calls to a server.
 * Requires:    socket.js
 * ------------------------------------------------------------------------ */

function Ajax(socket) {
    this.xmlhttp = new XMLHttpRequest();
    this.socket = socket;    
}

Ajax.prototype.send = function(method, callback, payload) {
    this.xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200 && callback) {
            callback(this.responseText);
        }
    }
    this.xmlhttp.open(method, this.socket.toString(), true);
    this.xmlhttp.send(payload);
}
