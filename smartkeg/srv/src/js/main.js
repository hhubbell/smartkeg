/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

function main() {
    var ajax = new Ajax('10.0.0.35', '8000');
    ajax.send('GET');
}


main();
