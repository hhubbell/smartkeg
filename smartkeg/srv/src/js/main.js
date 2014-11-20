/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

function setup_beer_menu() {
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
    
    client.source.onmessage = function(e) {
        var id = parseInt(e.lastEventId);

        if (id > client.last_update_id) {
            var payload = JSON.parse(e.data);
            
            client.last_update_id = id;
            client.kegs = []
            for (keg in payload) {
                keg_obj = new Keg(payload[keg])
                client.kegs.push(keg_obj);
            }
            client.set_beer_display('#serving');
            client.set_consumption_display('#consumption-graph');
            client.set_remaining_display('#remaining-graph');
            client.render();
            client.render_taps('#tap-form-taps');
        }
    }
    
    setup_beer_menu();    
    //client.host_get_brewer_list();
}


main();
