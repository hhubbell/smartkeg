/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

function setup_beer_menu() {
    var menu = document.querySelector('#beer-options');
    var tap_form = document.querySelector('#tap-form');
    var tap_item = menu.children[0];
    
    tap_item.addEventListener('click', function() {
        menu.style.display = 'none';
        tap_form.style.display = 'block'
    });
}

function main() {
    var protocol_re = new RegExp('^(http(s)?:\/\/)');
    var trailing_re = new RegExp('\/$');

    var host = document.URL.replace(protocol_re, '').replace(trailing_re, '');
    var port = 8000;
    
    var client = new SmartkegClient(new Socket(host, port));

    client.set_beer_display('#serving');
    client.set_consumption_display('#consumption-graph');
    client.set_remaining_display('#remaining-graph');
    
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

            client.render();
            client.render_taps('#tap-form-taps');
        }
    }

    //client.host_get_brewer_list();

    //setup_beer_menu();
}


main();
