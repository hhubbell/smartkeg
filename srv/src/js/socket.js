/* ------------------------------------------------------------------------ *
 * Filename:    socket.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: Manage socket information
 * ------------------------------------------------------------------------ */

/**
 * Defines a Socket Object.
 * @param host: The URL of the host device
 * @param port [optional]: The port on the host device
 */
function Socket(host, port) {
    this.host = host;
    this.port = port;
}

Socket.prototype.get_url = function() {
    return '//' + this.host + '/';
}

Socket.prototype.toString = function() {
    return '//' + this.host + ((this.port) ? ':' + this.port : '');
}
