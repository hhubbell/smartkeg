/* ------------------------------------------------------------------------ *
 * Filename:    socket.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: Manage socket information
 * ------------------------------------------------------------------------ */

function Socket(host, port) {
    this.host = host;
    this.port = port;
}

Socket.prototype.toString = function() {
    return '//' + this.host + ':' + this.port;
}
