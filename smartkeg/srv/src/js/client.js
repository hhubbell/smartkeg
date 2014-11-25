/* ------------------------------------------------------------------------ *
 * Filename:    client.js
 * Author:      Harrison Hubbell
 * Date:        11/11/2014
 * Description: Client side processing for the smartkeg system. Maintains
 *              a EventSource and Ajax connection with the server, and 
 *              renders graphs based on data it may receive.
 * Requires:    ajax.js
 *              keg.js
 *              graph.js
 * ------------------------------------------------------------------------ */

function SmartkegClient(socket) {
    this.source = new EventSource(socket.toString());
    this.ajax = new Ajax(socket.get_url());
    this.last_update_id = 0;
    this.render_index = 0;
    this.beer_display = null;
    this.consumption_display = null;
    this.remaining_display = null;

    this.brewers = null;
    this.brewer_offering = null;
    this.kegs = [];  
    this.menu = {};
}

SmartkegClient.prototype.set_beer_display = function(selector) {
    this.beer_display = document.querySelector(selector);
}

SmartkegClient.prototype.set_consumption_display = function(selector) {
    this.consumption_display = new ScatterPlot(selector);
}

SmartkegClient.prototype.set_remaining_display = function(selector) {
    this.remaining_display = new BarGraph(selector);
}

SmartkegClient.prototype.set_temperature_display = function(selector) {
    this.temperature_display = document.querySelector(selector);
}


// FIXME
SmartkegClient.prototype.set_menu = function(selector) {
    var self = this;
    this.menu.element = document.getElementById('beer-options');
    this.menu.options = this.menu.element.querySelectorAll('ul');
    this.menu.tap = {};
    this.menu.rate = {};
    
    this.menu.tap.option_element = document.getElementById('beer-option-tap');
    this.menu.tap.form = document.getElementById('tap-form');
    
    this.menu.rate.option_element = document.getElementById('beer-option-rate');
    this.menu.rate.form = document.getElementById('rate-form');

    this.menu.close_forms = document.getElementsByClassName('close-form');

    for (var i = 0; i < this.menu.close_forms.length; i++) {        
        this.menu.close_forms[i].addEventListener('click', function() {
            this.polyclosest('form').style.display = 'none';
            self.menu.element.style.display = 'block';
        });
    }

    this.menu.tap.option_element.addEventListener('click', function() {
        self.menu.element.style.display = 'none';
        self.menu.tap.form.style.display = 'block';
        
        var fieldsets = self.menu.tap.form.getElementsByTagName('fieldset');
        
        for (var i = 0; i < fieldsets.length; i++) {
            fieldsets[i].style.display = 'none';
        }
        
        fieldsets[0].style.display = 'inline-block';
    });

    this.menu.tap.form.onsubmit = function() {
        FOO = this;
        
        var beer_id = this.id.value;
        var beer_name = this.confirm_name.value;
        var beer_abv = this.confirm_abv.value;
        var beer_ibu = this.confirm_ibu.value;
        var keg_volume = this.confirm_volume.value;
        var passphrase = this.passphrase;

        var query_string = 'action=set&data=tap' +
            '&replace=' + self.menu.tap.replace +
            '&beer=' + beer_id +
            '&volume=' + keg_volume +
            '&passphrase=' + passphrase;

        console.log(query_string);
        

        self.ajax.send('POST', query_string);
        this.style.display = 'none';
        self.menu.element.style.display = 'block';
        return false;                               // Prevents page reload;
    }

    this.menu.rate.option_element.addEventListener('click', function() {
        self.menu.element.style.display = 'none';
        self.menu.rate.form.style.display = 'block';
    });
}

SmartkegClient.prototype.render = function() {
    this.render_beer();
    this.render_consumption();
    this.render_remaining();
    this.temperature_display.innerHTML = this.temperature;
}

SmartkegClient.prototype.render_beer = function() {
    var keg = this.kegs[this.render_index];

    for (var i = 0; i < this.beer_display.children.length; i++) {
        var node = this.beer_display.children[i]
        var content = node.getElementsByClassName('serving-content')[0];

        content.innerHTML = keg.beer[node.id] || '';
    }
}

SmartkegClient.prototype.render_consumption = function() {
    var keg = this.kegs[this.render_index];

    this.consumption_display.popall();
    this.consumption_display.clear();
    this.consumption_display.push(keg.consumption.days);
    this.consumption_display.set_radius(keg.consumption.radius);
    this.consumption_display.set_style(keg.consumption.style);
    this.consumption_display.render(true, true);
}

SmartkegClient.prototype.render_remaining = function() {
    var keg = this.kegs[this.render_index];
    
    this.remaining_display.popall();
    this.remaining_display.clear();   
    this.remaining_display.push(keg.remaining.value);
    this.remaining_display.render();
}



// THIS NEEDS REFACTORING BELOW

SmartkegClient.prototype.render_brewers = function(selector) {
    var NAME = 'brewer';
    var self = this;
    var element = document.querySelector(selector);

    element.polyempty();    
 
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

    element.polyempty();

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
            self.render_confirm('#tap-form-confirm', current);
            this.parentElement.style.display = 'none';
            //XXX Add animation
        });

        element.appendChild(radio);
        element.appendChild(label);
    }

    element.style.display = 'inline-block';    
}

SmartkegClient.prototype.render_confirm = function(selector, beer) {
    var self = this;
    var element = document.querySelector(selector);
    var beer_id = document.querySelector('input[name=id]') || document.createElement('input');

    beer_id.type = 'hidden';
    beer_id.name = 'id';
    beer_id.value = beer.id;
    element.appendChild(beer_id);
 
    document.getElementById('confirm-name').value = beer.name;
    document.getElementById('confirm-abv').value = beer.abv;
    document.getElementById('confirm-ibu').value = beer.ibu;

    element.style.display = 'inline-block';
}

SmartkegClient.prototype.render_tap_menu = function(selector) {
    var NAME = 'keg';
    var self = this;
    var element = document.querySelector(selector);

    element.polyempty()

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

                self.menu.tap.replace = radio.value;
            });
            
            this.parentElement.style.display = 'none';
        });
        
        element.appendChild(radio);
        element.appendChild(label);
    }
}
