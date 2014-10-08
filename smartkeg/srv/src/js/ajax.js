/* ------------------------------------------------------------------------ *
 * Filename:    ajax.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: Manage asyncronous calls to the server
 * ------------------------------------------------------------------------ */

function Ajax(host, port) {
    this.socket = new Socket(host, port);
    this.xmlhttp = new XMLHttpRequest();
    
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

Ajax.prototype.recv = function() {
    if (this.xmlhttp.readyState == 4 && this.xmlhttp.status == 200) {
        console.log(this.xmlhttp.responseText);
    }
}
