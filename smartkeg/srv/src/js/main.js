/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

function setup_beer_menu(client) {
    var menu = document.getElementById('beer-menu');
    var options = menu.querySelector('ul');
    var close_forms = menu.getElementsByClassName('close-form');

    var item_tap = document.getElementById('beer-option-tap');
    var item_rate = document.getElementById('beer-option-rate');

    var form_tap = document.getElementById('tap-form');
    var form_rate = document.getElementById('rate-form');

    // Close action
    Array.prototype.slice.call(close_forms, 0).forEach(function(i) { 
        i.addEventListener('click', function() {
            form = this.polyclosest('form');
            form.hidden = true;            
            fieldsets = Array.prototype.slice.call(form.getElementsByTagName('fieldset'), 0);
            fieldsets.slice(1).forEach(function(f) {
                f.hidden = true;
            });
            fieldsets[0].hidden = false;
            options.hidden = false;
        })
    });
    
    // Tap actions
    item_tap.addEventListener('click', function() {
        options.hidden = true;
        form_tap.hidden = false;
    });

    /*    
    this.menu.element = document.getElementById('beer-options');
    this.menu.tap = {};
    this.menu.rate = {};
    
    this.menu.tap.option_element = document.getElementById('beer-option-tap');
    this.menu.tap.form = document.getElementById('tap-form');
    
    this.menu.rate.option_element = document.getElementById('beer-option-rate');
    this.menu.rate.form = document.getElementById('rate-form');

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
    */

    // Rate actions
    item_rate.addEventListener('click', function() {
        options.hidden = true;
        form_rate.hidden = false;
    });

    form_rate.oninput = function() {
        this.ratingoutput.value = this.ratingslider.value
    }
    
    form_rate.onsubmit = function() {
        var query_string = "action=set" + 
            "&data=rating" +
            "&rating=" + this.ratingslider.value +
            "&text=" + this.ratingdescription.value;

        console.log(query_string);
        client.ajax.send('POST', query_string);
        return false;
    }
}

(function () {
    var PROTOCOL = new RegExp('^(http(s)?:\/\/)');
    var TRAILING = new RegExp('\/$');
    var HOST = document.URL.replace(PROTOCOL, '').replace(TRAILING, '');
    var PORT = 8000;
    
    var client = new SmartkegClient(new Socket(HOST, PORT));

    setup_beer_menu(client);
    
    client.set_temperature_display('#current-temperature');
    client.set_beer_display('#serving');
    client.set_consumption_display('#consumption-graph');
    client.set_remaining_display('#remaining-graph');

    client.source.onmessage = function(e) {
        var id = parseInt(e.lastEventId);
        var src = e.origin; 

        if (id > client.last_update_id) {
            var payload = JSON.parse(e.data);
            
            client.last_update_id = id;
            client.temperature = payload.temperature || '-- °F';
            client.kegs = payload.kegs
            client.render();
                
            // Merge these two into one?? Do it better??
            //client.set_menu('#beer-menu');                    
            client.render_tap_menu('#tap-form-taps');
        }
    }
})();
