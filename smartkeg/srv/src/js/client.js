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

SmartkegClient.prototype.clear = function(element) {
    while (element.lastChild) {
        element.removeChild(element.lastChild);
    }
}

SmartkegClient.prototype.render = function() {
    this.kegs[this.render_index].render_beer();
    this.kegs[this.render_index].render_consumption();
    this.kegs[this.render_index].render_remaining();
    this.temperature_display.innerHTML = this.temperature;
}

SmartkegClient.prototype.render_brewers = function(selector) {
    var NAME = 'brewer';
    var self = this;
    var element = document.querySelector(selector);

    this.clear(element);    
 
    for (var i = 0; i < this.brewers.length; i++) {
        var current = this.brewers[i];
        var radio = document.createElement('input');
        var label = document.createElement('label');
        radio.type = 'radio';
        radio.name = NAME;
        radio.value = current.id;
        radio.id = NAME + '-' + current.name;

        label.htmlFor = NAME + '-' + current.name;
        label.innerHTML = current.name;

        console.log(current.id);

        radio.addEventListener('click', function() {
            self.ajax.send('POST', 'action=get&data=offering&brewer=' + this.value).then(function(response) {
                self.brewer_offering = JSON.parse(response);
                console.log(self.brewer_offering);
                self.render_brewer_offering('#tap-form-beer');
            });

            this.parentElement.style.display = 'none';            
        });

        element.appendChild(radio);
        element.appendChild(label);
    }

    element.style.display = 'inline-block';
}

SmartkegClient.prototype.render_brewer_offering = function(selector) {
    var NAME = 'beer';
    var self = this;
    var element = document.querySelector(selector);

    console.log(this);

    this.clear(element);

    for (var i = 0; i < this.brewer_offering.length; i++) {
        var current = this.brewer_offering[i];
        var radio = document.createElement('input');
        var label = document.createElement('label');
        radio.type = 'radio';
        radio.name = NAME;
        radio.value = current.id;
        radio.id = NAME + '-' + current.id;

        label.htmlFor = NAME + '-' + current.id;
        label.innerHTML = current.name;

        console.log(current.id);

        radio.addEventListener('click', function() {
            console.log('click');
            //XXX Do something here
            //XXX Add animation
        });

        element.appendChild(radio);
        element.appendChild(label);
    }

    element.style.display = 'inline-block';    
}

SmartkegClient.prototype.render_tap_menu = function(selector) {
    var NAME = 'keg';
    var self = this;
    var element = document.querySelector(selector);

    this.clear(element);

    for (var i = 0; i < this.kegs.length; i ++) {
        var current = this.kegs[i];
        var radio = document.createElement('input');
        var label = document.createElement('label');
        radio.type = 'radio';
        radio.name = NAME;
        radio.value = current.id;
        radio.id = NAME + '-' + current.id;

        label.htmlFor = NAME + '-' + current.id;
        label.innerHTML = current.beer.name + ' ' + (current.remaining.value * 100).toFixed(2) + '%';
        
        radio.addEventListener('click', function() {
            self.ajax.send('POST', 'action=get&data=brewers').then(function(response) {
                self.brewers = JSON.parse(response);
                self.render_brewers('#tap-form-brewer');
            });
            
            this.parentElement.style.display = 'none';
        });
        
        element.appendChild(radio);
        element.appendChild(label);
    }
}
