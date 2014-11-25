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

    /**
     * @Author:         Harrison Hubbell
     * @Created:        11/25/2014
     * @Description:    Verifies the payload from the event source
     *                  meets the requirements needed. Requirements:
     *                  
     *                  1. temperature
     *                  2. kegs
     *                      a. beer
     *                      b. consumption
     *                      c. remaining
     */
    function verify_payload(p) {
        return !!(
            p.temperature &&
            p.kegs.beer &&
            p.kegs.consumption &&
            p.kegs.remaining
        );
    }
    
    var client = new SmartkegClient(new Socket(HOST, PORT));
    
    client.set_temperature_display('#current-temperature');
    client.set_beer_display('#serving');
    client.set_consumption_display('#consumption-graph');
    client.set_remaining_display('#remaining-graph');
    
    client.source.onmessage = function(e) {
        var id = parseInt(e.lastEventId);
        var src = e.origin;

        if (id > client.last_update_id && src == client.socket.toString()) {
            var payload = JSON.parse(e.data);

            if (verify_payload(payload)) {
                client.last_update_id = id;
                client.temperature = payload.temperature;
                client.kegs = payload.kegs
                client.render();
                
                // Merge these two into one?? Do it better??
                //client.set_menu('#beer-menu');                    
                client.render_tap_menu('#tap-form-taps');
            }
        }
    }
})();
