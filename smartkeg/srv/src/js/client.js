/* ------------------------------------------------------------------------ *
 * Filename:    client.js
 * Author:      Harrison Hubbell
 * Date:        11/11/2014
 * Description: Client side processing for the smartkeg system. Maintains
 *              a EventSource and Ajax connection with the server, and 
 *              renders graphs based on data it may receive.
 * Requires:    ajax.js
 *              keg.js
 * ------------------------------------------------------------------------ */

function SmartkegClient(socket) {
    this.source = new EventSource(socket.toString());
    this.ajax = new Ajax(socket);
    this.last_update_id = 0;
    this.render_index = 0;
    this.beer_display = null;
    this.consumption_display = null;
    this.remaining_display = null;
    this.kegs = []    
}

SmartkegClient.prototype.set_beer_display = function(selector) {
    this.beer_display = selector;
}

SmartkegClient.prototype.set_consumption_display = function(selector) {
    this.consumption_display = selector;
}

SmartkegClient.prototype.set_remaining_display = function(selector) {
    this.remaining_display = selector;
}

SmartkegClient.prototype.render = function() {
    console.log(this)
    this.kegs[this.render_index].render_beer(this.beer_display);
    this.kegs[this.render_index].render_consumption(this.consumption_display);
    this.kegs[this.render_index].render_remaining(this.remaining_display);    
}
