/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

function example(response) {
    console.log(response);
    var jso = JSON.parse(response);

    render_consumption_graph('#consumption-graph', jso.consumption);
    render_volume_remaining('#remaining-graph', jso.remaining);
    render_beer_info(jso.beer_info);
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

function render_beer_info(set) {
    document.querySelector('#brand').innerHTML = set.brand;
    document.querySelector('#name').innerHTML = set.name;
    document.querySelector('#abv').innerHTML = set.ABV;
    document.querySelector('#rating').innerHTML = set.rating;
    
}

function main() {
    //var ajax = new Ajax('10.0.0.35', '8000');
    var source = new EventSource('http://10.0.0.35:8000');

    source.addEventListener('init', function(e) {
        console.log('Connection Initialized');
        example(e.data);
        e.target.removeEventListener(e.type, this);
    }

    source.addEventListener('update', function(e) {
        console.log('Update Received, Re-rendering');
        example(e.data);
    });
    

    //ajax.send('GET', example);
}


main();
