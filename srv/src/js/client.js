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
    this.host = socket.url;
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

SmartkegClient.prototype.set_beer_display = function (selector) {
    this.beer_display = document.querySelector(selector);
}

SmartkegClient.prototype.set_consumption_display = function (selector) {
    this.consumption_display = new ScatterPlot(selector);
}

SmartkegClient.prototype.set_remaining_display = function (selector) {
    this.remaining_display = new BarGraph(selector);
}

SmartkegClient.prototype.set_temperature_display = function (selector) {
    this.temperature_display = document.querySelector(selector);
}

/**
 * SmartkegClient.setFormCloseTrigger: Set trigger elements for
 * closing forms and add event listeners
 * @param selector: Trigger selector;
 */
SmartkegClient.prototype.setFormCloseTrigger = function (selector) {
    var self = this;
    var triggers = document.querySelectorAll(selector);
    
    Array.prototype.forEach.call(triggers, function (el) {
        el.addEventListener('click', function () {
            self.closeForm(this.polyclosest('form');
        }
    });
}

/**
 * SmartkegClient.closeForm: Hide form and all children except firstChild
 * @param form: Form to close
 */
SmartkegClient.prototype.closeForm = function (form) {
    var children = Array.prototype.slice.call(form.children, 0);
    
    form.hidden = true;

    children[0].hidden = false;
    children.slice(1).forEach(function (el) {
        el.hidden = true;
    }
}


SmartkegClient.prototype.render = function () {
    this.render_beer();
    this.render_consumption();
    this.render_remaining();
    this.temperature_display.innerHTML = this.temperature + ' °F';
}

SmartkegClient.prototype.render_beer = function () {
    var keg = this.kegs[this.render_index];

    for (var i = 0; i < this.beer_display.children.length; i++) {
        var node = this.beer_display.children[i]
        var content = node.getElementsByClassName('serving-content')[0];

        content.innerHTML = keg.beer[node.id] || '';
    }
}

SmartkegClient.prototype.render_consumption = function () {
    var keg = this.kegs[this.render_index];
    
    this.consumption_display.clear();
    bottom = this.consumption_display.render_seasonal_trendline(keg.volume, 0, 0, (1 - keg.remaining.value), keg.falling, 'values');

    this.consumption_display.render_seasonal_trendline(keg.volume, bottom, (1 - keg.remaining.value), keg.remaining.value, keg.consumption.days, 'prediction');

}

SmartkegClient.prototype.render_remaining = function () {
    var keg = this.kegs[this.render_index];
    
    this.remaining_display.popall();
    this.remaining_display.clear();   
    this.remaining_display.push(keg.remaining.value);
    this.remaining_display.render();
}



// THIS NEEDS REFACTORING BELOW

SmartkegClient.prototype.render_brewers = function (selector) {
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

        radio.addEventListener('click', function () {
            polyfetch(this.host + 'api/get/beer?brewer_id=' + this.value).then(function (response) {
                self.brewer_offering = JSON.parse(response);
                self.render_brewer_offering('#tap-form-beer');
            }

            this.parentElement.hidden = true;
        });

        element.appendChild(radio);
        element.appendChild(label);
    }

    element.hidden = false;
}

SmartkegClient.prototype.render_brewer_offering = function (selector) {
    var NAME = 'beer';
    var self = this;
    var element = document.querySelector(selector);

    element.polyempty();

    this.brewer_offering.forEach(function (current) {
        var radio = document.createElement('input');
        var label = document.createElement('label');
        radio.type = 'radio';
        radio.name = NAME;
        radio.value = current.id;
        radio.id = NAME + '-' + current.id;

        label.htmlFor = NAME + '-' + current.id;
        label.innerHTML = current.name;

        radio.addEventListener('click', function () {
            self.render_confirm('#tap-form-confirm', current);
            this.parentElement.hidden = true;
            //XXX Add animation
        });

        element.appendChild(radio);
        element.appendChild(label);
    });

    element.hidden = false;
}

SmartkegClient.prototype.render_confirm = function (selector, beer) {
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

    element.hidden = false;
}

SmartkegClient.prototype.render_tap_menu = function (selector) {
    var NAME = 'keg';
    var self = this;
    var element = document.querySelector(selector);

    element.polyempty();

    for (var i = 0; i < this.kegs.length; i++) {
        var current = this.kegs[i];
        var radio = document.createElement('input');
        var label = document.createElement('label');
 
        radio.type = 'radio';
        radio.name = NAME;
        radio.value = current.id;
        radio.id = NAME + '-' + current.id;

        label.htmlFor = NAME + '-' + current.id;
        label.innerHTML = "Tap " + (i + 1) + ": " + current.beer.name + ' (' + (current.remaining.value * 100).toFixed(2) + '% remaining)';
        
        radio.addEventListener('click', function () {
            self.replace = this.value;

            polyfetch(this.host + 'api/get/brewer').then(function (response) {
                self.brewers = JSON.parse(response);
                self.render_brewers('#tap-form-brewer');
            }
            
            this.parentElement.hidden = true;
        });
        
        element.appendChild(radio);
        element.appendChild(label);
    }
}
