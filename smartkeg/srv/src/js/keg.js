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

Keg.prototype.render_beer = function(selector) {
    element = document.querySelector(selector);

    for (var i = 0; i < element.children.length; i++) {
        var node = element.children[i]
        var data_content = document.createElement('span');
        
        data_content.innerHTML = this.beer[node.id] || '';

        node.appendChild(data_content);
    }
}

Keg.prototype.render_consumption = function(selector) {
    var graph = new ScatterPlot(selector);
    graph.add_set(this.consumption);
    graph.set_independent_variable('days');
    graph.set_point_radius(this.consumption.radius);
    graph.render(false, true, true);
}

Keg.prototype.render_remaining = function(selector) {
    var graph = new BarGraph(selector);
    graph.add_category(this.remaining);
    graph.render();
}
