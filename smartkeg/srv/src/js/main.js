/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

// XXX Depreciated
function setup_menu() {
    var menu = document.getElementById('beer-options');
    var tap_item = document.getElementById('beer-option-tap');
    var rate_item = document.getElementById('beer-option-rate');
    var tap_form = document.getElementById('tap-form');
    var rate_form = document.getElementById('rate-form');
    var close_form = document.getElementsByClassName('close-form')

    for (var i = 0; i < close_form.length; i++) {
        close_form[i].addEventListener('click', function() {
            this.parentNode.style.display = 'none';
            menu.style.display = 'block';
        });
    }

    tap_item.addEventListener('click', function() {
        menu.style.display = 'none';
        tap_form.style.display = 'block';
        
        var fieldsets = tap_form.getElementsByTagName('fieldset');
        
        for (var i = 0; i < fieldsets.length; i++) {
            fieldsets[i].style.display = 'none';
        }
        fieldsets[0].style.display = 'inline-block';
    });

    rate_item.addEventListener('click', function() {
        menu.style.display = 'none';
        rate_form.style.display = 'block';
    });


}

function main() {
    var protocol_re = new RegExp('^(http(s)?:\/\/)');
    var trailing_re = new RegExp('\/$');

    var host = document.URL.replace(protocol_re, '').replace(trailing_re, '');
    var port = 8000;
    
    var client = new SmartkegClient(new Socket(host, port));
    
    client.set_temperature_display('#current-temperature');
    client.set_menu();    
    
    client.source.onmessage = function(e) {
        var id = parseInt(e.lastEventId);

        if (id > client.last_update_id) {
            var payload = JSON.parse(e.data);

            console.log(payload);
            
            client.temperature = payload.temperature;
            client.last_update_id = id;
            client.kegs = []
            
            for (k in payload.kegs) {
                keg = new Keg(payload.kegs[k]);
                keg.set_beer_display('#serving');
                keg.set_consumption_display('#consumption-graph');
                keg.set_remaining_display('#remaining-graph');

                console.log(keg);
                client.kegs.push(keg);
            }
            
            client.render();
            client.render_tap_menu('#tap-form-taps');
        }
    }
    
    //client.host_get_brewer_list();
}


main();
