/* ------------------------------------------------------------------------ *
 * Filename:    keg.js
 * Author:      Harrison Hubbell
 * Date:        11/11/2014
 * Description: Maintains information regarding kegs, particularly the beer,
 *              consumption, and amount remaining information.
 * ------------------------------------------------------------------------ */

function Keg(keg_obj) {
    this.id = keg_obj.id;
    this.beer = keg_obj.beer;
    this.consumption = keg_obj.consumption;
    this.remaining = keg_obj.remaining;
}
