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

    for (attribute in this.beer) {
        data_wrapper = document.createElement('div');
        data_title = document.createElement('span');
        data_content = document.createElement('span');

        data_wrapper.classList.add('serving-data');
        data_content.id = attribute;

        data_title.innerHTML = attribute;
        data_content.innerHTML = this.beer[attribute];

        data_wrapper.appendChild(data_title);
        data_wrapper.appendChild(data_content);

        element.appendChild(data_wrapper);
    }
}

Keg.prototype.render_consumption = function(selector) {
    var graph = new ScatterPlot(selector);
    graph.add_set(this.consumption);
    graph.set_point_radius(3);
    graph.calculate_means();
    graph.render(true, true, true);
}

Keg.prototype.render_remaining = function(selector) {
    var graph = new BarGraph(selector);
    graph.add_category(this.remaining);
    graph.render();
}
