/*
 * Filename:    socket.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: Manage socket information
 */

/**
 * Defines a Socket Object.
 * @param host:     The URL of the host device
 * @optional port:  The port on the host device
 */
function Socket(host, port) {
    this.host = host;
    this.port = port;
    this.url = '//' + this.host + '/';
}

/**
 * Socket.toString: Return the full string representation
 * of the socket
 * @return: Socket string.
 */
Socket.prototype.toString = function() {
    return '//' + this.host + ((this.port) ? ':' + this.port : '');
}
