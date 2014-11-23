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
    this.ajax = new Ajax(socket.get_url());
    this.last_update_id = 0;
    this.render_index = 0;
    this.brewers = null;
    this.brewer_offering = null;
    this.kegs = []    
}

SmartkegClient.prototype.set_temperature_display = function(selector) {
    this.temperature_display = document.querySelector(selector);
}

SmartkegClient.prototype.host_get_brewers = function() {
    var self = this;
    console.log(this);

    console.log('click sent');
    this.ajax.send('POST', 'action=get&data=brewers').then(function(response) {
        self.brewers = response;
    });
}

SmartkegClient.prototype.host_get_brewer_offering = function(brewer) {
    this.ajax.send('POST', this.handle_brewer_offering, 'action=get&data=offering&brewer=' + brewer);
}

SmartkegClient.prototype.render = function() {
    this.kegs[this.render_index].render_beer();
    this.kegs[this.render_index].render_consumption();
    this.kegs[this.render_index].render_remaining();
    this.temperature_display.innerHTML = this.temperature;
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

SmartkegClient.prototype.render_tap_menu = function(selector) {
    var NAME = 'kegs';
    var self = this;
    var element = document.querySelector(selector);

    for (var i = 0; i < this.kegs.length; i ++) {
        var radio = document.createElement('input');
        var label = document.createElement('label');
        radio.type = 'radio';
        radio.name = NAME;
        radio.value = this.kegs[i].id;
        radio.id = this.kegs[i].id;

        label.htmlFor = this.kegs[i].id;
        label.innerHTML = this.kegs[i].beer.name + ' ' + (this.kegs[i].remaining.value * 100).toFixed(2) + '%';
        
        radio.addEventListener('click', function() {self.host_get_brewers()});
        //label.addEventListener('click', function() {self.host_get_brewers()});
        
        element.appendChild(radio);
        element.appendChild(label);
    }
}
