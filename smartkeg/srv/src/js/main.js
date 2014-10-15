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
    /*var*/ graph = new Graph(selector);
    graph.add_point(2,3);
    graph.add_point(100,23);
    graph.add_point(24,37);
    graph.add_point(125,73);
    graph.render('rect', 2);
    

}

function main() {
    var ajax = new Ajax('10.0.0.35', '8000');
    //ajax.send('GET', example);
    render_consumption_graph('#consumption-graph');
}


main();
