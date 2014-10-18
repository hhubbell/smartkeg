/* ------------------------------------------------------------------------ *
 * Filename:    main.js
 * Author:      Harrison Hubbell
 * Date:        10/07/2014
 * Description: The main method
 * ------------------------------------------------------------------------ */

function example(response) {
    console.log(response);
    var jso = JSON.parse(response);

    document.querySelector('#name').innerHTML = jso.name;
    document.querySelector('#age').innerHTML = jso.age;
    document.querySelector('#gender').innerHTML = jso.gender;

}

function render_consumption_graph(selector) {
    graph = new ScatterPlot(selector);
    
    //This is an example of the data recieved from the xmlhttp request.
    test_set = {
        'x': {
            50: {
                'y':[3, 5, 17, 23, 8, 6, 13, 14, 5, 16],
                'mean': null,
            },
            150: {
                'y':[6, 3, 7, 13, 16, 8, 16, 3, 4, 6],
                'mean': null,
            },
            250: {
                'y':[3, 8, 17, 9, 16, 8, 16, 13, 10, 6],
                'mean': null,
            },
            350: {
                'y':[9, 18, 56, 13, 6, 28, 16, 23, 24, 36],
                'mean': null,
            },
            450: {
                'y':[33, 43, 67, 53, 56, 48, 46, 33, 44, 36],
                'mean': null,
            },
            550: {
                'y':[93, 83, 77, 93, 96, 98, 116, 63, 64, 36],
                'mean': null,
            },
            650: {
                'y':[83, 83, 77, 93, 96, 98, 90, 43, 44, 46],
                'mean': null,
            }
        },
        'radius': 2,
        'style': 'circle'
    }

    graph.add_set(test_set);
    graph.calculate_means();
    graph.render(true, true, true, true);
}

function render_volume_remaining(selector) {
    graph = new BarGraph(selector);

    // Example Data
    test_set = {
        'y': 50 //Percent
    }

    graph.add_category(test_set);
    graph.render();
}

function main() {
    var ajax = new Ajax('10.0.0.35', '8000');
    //ajax.send('GET', example);
    render_consumption_graph('#consumption-graph');
    render_volume_remaining('#remaining-graph');
}


main();
