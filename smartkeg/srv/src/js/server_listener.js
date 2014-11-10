/* ------------------------------------------------------------------------ *
 * Filename:    server_listener.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Connects to a server socket and listens for Server Sent Events
 * ------------------------------------------------------------------------ */

function ServerListener(host) {
    this.source = new EventSource(host.toString());
    this.update_id = 0;
}
