/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

(function () {
    var PROTOCOL = new RegExp('^(http(s)?:\/\/)');
    var TRAILING = new RegExp('\/$');
    var HOST = document.URL.replace(PROTOCOL, '').replace(TRAILING, '');
    var PORT = 8000;
    
    var client = new SmartkegClient(new Socket(HOST, PORT));

    client.set_temperature_display('#current-temperature');
    client.set_beer_display('#serving');
    client.set_consumption_display('#consumption-graph');
    client.set_remaining_display('#remaining-graph');

    // -------------------
    // Setup Beer Menu Items
    // -------------------
    client.menu = document.getElementById('beer-menu');
    client.options = client.menu.querySelector('ul');
    client.close_forms = client.menu.getElementsByClassName('close-form');
    
    client.item_tap = document.getElementById('beer-option-tap');
    client.item_rate = document.getElementById('beer-option-rate');

    client.form_tap = document.getElementById('tap-form');
    client.form_rate = document.getElementById('rate-form');

    // CLOSE ACTION
    Array.prototype.slice.call(client.close_forms, 0).forEach(function(i) { 
        i.addEventListener('click', function() {
            form = this.polyclosest('form');
            form.hidden = true;            
            fieldsets = Array.prototype.slice.call(form.getElementsByTagName('fieldset'), 0);
            fieldsets.slice(1).forEach(function(f) {
                f.hidden = true;
            });
            fieldsets[0].hidden = false;
            client.options.hidden = false;
        })
    });

    // TAP ACTIONS
    client.item_tap.addEventListener('click', function() {
        client.options.hidden = true;
        client.form_tap.hidden = false;
    });

    client.form_tap.onsubmit = function() {
        var self = this;

        var query_string = encodeURI(
            'action=set&data=tap' +
            '&replace=' + client.replace +
            '&beer=' + this.id.value +
            '&volume=' + this.confirm_volume.value +
            '&passphrase=' + this.passphrase
        );

        console.log(query_string);
        
        client.ajax.send('POST', query_string).then(function(response) {
            self.reset();
            self.hidden = true;
            fieldsets = Array.prototype.slice.call(self.getElementsByTagName('fieldset'), 0);
            fieldsets.slice(1).forEach(function(f) {
                f.hidden = true;
            });
            fieldsets[0].hidden = false;
            client.options.hidden = false;
        });
        return false;
    }

    // RATE ACTIONS
    client.item_rate.addEventListener('click', function() {
        client.options.hidden = true;
        client.form_rate.hidden = false;
    });

    client.form_rate.oninput = function() {
        this.ratingoutput.value = this.ratingslider.value
    }
    
    client.form_rate.onsubmit = function() {
        var self = this;
        var query_string = encodeURI(
            "action=set" + 
            "&data=rate" +
            "&beer=" + client.kegs[client.render_index].beer.id +
            "&rating=" + this.ratingslider.value +
            "&comments=" + this.ratingdescription.value
        );

        console.log(query_string);
        client.ajax.send('POST', query_string).then(function(response) {
            self.reset();
            self.hidden = true;            
            client.options.hidden = false;
        });
        return false;
    }

    // -------------------
    // EventSource Handling
    // -------------------
    client.source.onmessage = function(e) {
        var id = parseInt(e.lastEventId);
        var src = e.origin; 

        if (id > client.last_update_id) {
            var payload = JSON.parse(e.data);
            
            console.log(payload);

            client.last_update_id = id;
            client.temperature = payload.temperature || '-- °F';
            client.kegs = payload.kegs
            client.render();                 
            client.render_tap_menu('#tap-form-taps');
        }
    }

    // -------------------
    // Window Resize Handling
    // -------------------
    window.onresize = function() {
        client.render_consumption();
        client.render_remaining();
    }

})();
