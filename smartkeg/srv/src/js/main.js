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
    graph.calculate_set_means();
    graph.render_set_points();
    graph.render_set_seasonal_trendline();    
    graph.render_set_means();
    
    /*graph.add_point({'x':100, 'y':3, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':23, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':37, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':73, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':63, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':83, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':76, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':53, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':54, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':55, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':56, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':57, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':58, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':59, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':52, 'style':'circle', 'radius':2});
    graph.add_point({'x':100, 'y':51, 'style':'circle', 'radius':2});
    
    graph.add_point({'x':200, 'y':63, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':83, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':77, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':93, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':6, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':8, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':16, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':53, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':54, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':55, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':36, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':37, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':38, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':79, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':12, 'style':'circle', 'radius':2});
    graph.add_point({'x':200, 'y':21, 'style':'circle', 'radius':2});

    graph.add_point({'x':300, 'y':93, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':83, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':77, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':93, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':96, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':98, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':116, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':63, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':64, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':65, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':36, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':37, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':38, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':69, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':12, 'style':'circle', 'radius':2});
    graph.add_point({'x':300, 'y':91, 'style':'circle', 'radius':2});
    
    graph.calculate_point_means();
    graph.render_point_points();
    graph.render_seasonal_trendline();    
    graph.render_point_means('circle', 2);
    
    */
}

function main() {
    var ajax = new Ajax('10.0.0.35', '8000');
    //ajax.send('GET', example);
    render_consumption_graph('#consumption-graph');
}


main();
