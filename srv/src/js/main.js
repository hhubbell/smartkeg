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
    //client.close_forms = client.menu.getElementsByClassName('close-form');
    
    client.item_tap = document.getElementById('beer-option-tap');
    client.item_rate = document.getElementById('beer-option-rate');

    client.form_tap = document.getElementById('tap-form');
    client.form_rate = document.getElementById('rate-form');

    client.setFormCloseTrigger('.close-form');

    // TAP ACTIONS
    client.item_tap.addEventListener('click', function () {
        client.options.hidden = true;
        client.form_tap.hidden = false;
    });

    client.form_tap.onsubmit = function () {
        var self = this;

        var query = encodeURI(
            'api/set/keg?replace=' + client.replace +
            '&beer_id=' + this.id.value +
            '&volume=' + this.confirm_volume.value
        );

        console.log(query);
        
        polyfetch(query, {method: 'POST'}).then(function (response) {
            self.reset()
            client.closeForm(self);
            client.options.hidden = false;
        });
        
        return false;
    }

    // RATE ACTIONS
    client.item_rate.addEventListener('click', function () {
        client.options.hidden = true;
        client.form_rate.hidden = false;
    });

    client.form_rate.oninput = function () {
        this.ratingoutput.value = this.ratingslider.value
    }
    
    client.form_rate.onsubmit = function () {
        var self = this;
        var query = encodeURI(
            "api/set/rating" + 
            "?beer_id=" + client.kegs[client.render_index].beer.id +
            "&rating=" + this.ratingslider.value +
            "&comments=" + this.ratingdescription.value
        );

        console.log(query);
        polyfetch(query, {method: 'POST'}).then(function (response) {
            self.reset();
            self.hidden = true;            
            client.options.hidden = false;
        });
        
        return false;
    }

    // -------------------
    // EventSource Handling
    // -------------------
    client.source.onmessage = function (e) {
        var id = parseInt(e.lastEventId);
        var src = e.origin; 

        if (id > client.last_update_id) {
            var payload = JSON.parse(e.data);
            
            console.log(payload);

            client.last_update_id = id;
            client.temperature = (payload.temperature) ? payload.temperature.toFixed(2) : '--';
            client.kegs = payload.kegs
            client.render();                 
            client.render_tap_menu('#tap-form-taps');
        }
    }

    // -------------------
    // Window Resize Handling
    // -------------------
    window.onresize = function () {
        client.render_consumption();
        client.render_remaining();
    }

}());
