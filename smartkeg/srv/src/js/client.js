/* ------------------------------------------------------------------------ *
 * Filename:    client.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Client side processing for the smartkeg system. Maintains
 *              a ServerListener and Ajax connection with the server, and 
 *              renders graphs based on data it may receive.
 * Requires:    ajax.js
 *              server_listner.js
 * ------------------------------------------------------------------------ */

function SmartkegClient(socket) {
    this.listener = new ServerListner(socket);
    this.ajax = new Ajax(socket);
}
