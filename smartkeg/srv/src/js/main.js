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

function main() {
    var ajax = new Ajax('10.0.0.35', '8000');
    ajax.send('GET', example);
}


main();
