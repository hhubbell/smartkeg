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
    this.brewers = null;
    this.brewer_offering = null;
    this.beer_display = null;
    this.consumption_display = null;
    this.remaining_display = null;
    this.kegs = []    
}

SmartkegClient.prototype.handle_brewer_list = function(list) {
    this.brewers = list;
    this.render_brewer_list('#tap-form-brewer ul');
}

SmartkegClient.prototype.handle_brewer_offering = function(list) {
    this.brewer_offering = list;
    this.render_brewer_offering('#tap-form-beer ul');
}

SmartkegClient.prototype.host_get_brewer_list = function() {
    this.ajax.send('POST', this.handle_brewer_list, 'data=brewers');
}

SmartkegClient.prototype.host_get_brewer_offering = function(brewer) {
    this.ajax.send('POST', this.handle_brewer_offering, 'data=offering&brewer=' + brewer);
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

SmartkegClient.prototype.render_brewer_list = function(selector) {
    var element = document.querySelector(selector);
    
    for (var i = 0; i < this.brewers.length; i++) {
        var list_item = document.createElement('li');
        
        list_item.innerHTML = this.brewers[i];
        list_item.addEventListener('click', function() {
            this.host_get_brewer_offering(this.brewers[i]);
            //XXX Add Animation
        });

        element.appendChild(list_item);
    }
}

SmartkegClient.prototype.render_brewer_offering = function(selector) {
    var element = document.querySelector(selector)

    for (var i = 0; i < this.brewer_offering.length; i++) {
        var list_item = document.createElement('li');

        list_item.innerHTML = this.brewer_offering[i];
        list_item.addEventListener('click', function() {
            //XXX Do something here
            //XXX Add animation
        });

        element.appendChild(list_item);
    }
}

SmartkegClient.prototype.render_taps = function(selector) {
    var NAME = 'kegs';
    var element = document.querySelector(selector);

    for (var i = 0; i < this.kegs.length; i ++) {
        var radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = NAME;
        radio.value = this.kegs[i].beer.name;
        radio.innerHTML = this.kegs[i].beer.name + ' ' + this.kegs[i].remaining.y;

        element.appendChild(radio);
    }
}
