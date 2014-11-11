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
    var graph = new ScatterPlot(selector);
    graph.add_set(set);
    graph.set_point_radius(3);
    graph.calculate_means();
    graph.render(true, true, true);
    console.log(graph);
    
}

function render_volume_remaining(selector, set) {
    var graph = new BarGraph(selector);
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
    var client = new SmartkegClient(new Socket('10.0.0.35', 8000));

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

            client.render()
        }
    }
}


main();
