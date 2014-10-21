/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

function example(response) {
    console.log(response);
    var jso = JSON.parse(response);

    render_consumption_graph('#consumption-graph', jso.consumption)
    render_volume_remaining('#remaining-graph', jso.remaining)
}

function render_consumption_graph(selector, set) {
    graph = new ScatterPlot(selector);
    graph.add_set(set);
    graph.calculate_means();
    graph.render(true, true, true, true);
}

function render_volume_remaining(selector, set) {
    graph = new BarGraph(selector);
    graph.add_category(set);
    graph.render();
}

function main() {
    var ajax = new Ajax('10.0.0.35', '8000');
    ajax.send('GET', example);
    //render_consumption_graph('#consumption-graph');
    //render_volume_remaining('#remaining-graph');
}


main();
