/* ------------------------------------------------------------------------ *
 * Filename:    keg.js
 * Author:      Harrison Hubbell
 * Date:        11/11/2014
 * Description: Maintains information regarding kegs, particularly the beer,
 *              consumption, and amount remaining information.
 * Requires:    graph.js
 * ------------------------------------------------------------------------ */

function Keg(keg_obj) {
    console.log(keg_obj)
    this.beer = keg_obj.beer;
    this.consumption = keg_obj.consumption;
    this.remaining = keg_obj.remaining;
}

Keg.prototype.set_beer_display = function(selector) {
    this.beer_display = document.querySelector(selector);
}

Keg.prototype.set_consumption_display = function(selector) {
    this.consumption_display = new ScatterPlot(selector);
}

Keg.prototype.set_remaining_display = function(selector) {
    this.remaining_display = new BarGraph(selector);
}

Keg.prototype.render_beer = function() {
    for (var i = 0; i < this.beer_display.children.length; i++) {
        var node = this.beer_display.children[i]
        var data_content = document.createElement('span');

        data_content.innerHTML = this.beer[node.id] || '';
        node.appendChild(data_content);
    }
}

Keg.prototype.render_consumption = function() {
    this.consumption_display.popall();
    this.consumption_display.clear();
    this.consumption_display.push(this.consumption.days);
    this.consumption_display.set_radius(this.consumption.radius);
    this.consumption_display.set_style(this.consumption.style);
    this.consumption_display.render(true, true);
}

Keg.prototype.render_remaining = function() {
    this.remaining_display.popall();
    this.remaining_display.clear();
    this.remaining_display.push(this.remaining.value);
    this.remaining_display.render();
}
