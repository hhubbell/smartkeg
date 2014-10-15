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
    var graph = new Graph(selector);
    
    //This is an example of the data recieved from the xmlhttp request.
    test_set = {
        'x': {
            100: {
                'y':[3, 23, 37, 63, 83, 76, 53, 54, 55, 56],
                'mean': null,
            },
            200: {
                'y':[63, 83, 77, 93, 6, 8, 16, 53, 54, 36],
                'mean': null,
            },
            300: {
                'y':[93, 83, 77, 93, 96, 98, 116, 63, 64, 36],
                'mean': null,
            }
        },
        'radius': 2,
        'style': 'circle'
    }

    graph.add_set(test_set);
    graph.calculate_means();
    graph.render_sets();
    graph.render_seasonal_trendline();    
    graph.render_means();
}

function main() {
    var ajax = new Ajax('10.0.0.35', '8000');
    //ajax.send('GET', example);
    render_consumption_graph('#consumption-graph');
}


main();
