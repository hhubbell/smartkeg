/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

function main() {
    var PROTOCOL = new RegExp('^(http(s)?:\/\/)');
    var TRAILING = new RegExp('\/$');
    var HOST = document.URL.replace(PROTOCOL, '').replace(TRAILING, '');
    var PORT = 8000;
    
    var client = new SmartkegClient(new Socket(HOST, PORT));
    
    client.set_temperature_display('#current-temperature');
    client.set_beer_display('#serving');
    client.set_consumption_display('#consumption-graph');
    client.set_remaining_display('#remaining-graph');
    //client.set_menu('#beer-menu');    
    
    client.source.onmessage = function(e) {
        var id = parseInt(e.lastEventId);

        if (id > client.last_update_id) {
            var payload = JSON.parse(e.data);

            console.log(payload);

            client.kegs.length = 0;
            client.temperature = payload.temperature;
            client.last_update_id = id;
 
            for (var i = 0; i < payload.kegs.length; i++) {
                client.kegs.push(new Keg(payload.kegs[i]));
            }
            
            client.render();
            client.render_tap_menu('#tap-form-taps');
        }
    }
}


main();
