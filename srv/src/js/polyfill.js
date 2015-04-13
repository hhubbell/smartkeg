/*
 * Filename:    polyfill.js
 * Author:      Harrison Hubbell
 * Date:        11/24/2014
 * Description: Polyfills for needed  functionality
 */

/**
 * polyclosest: Find the closest element from selector. Requires
 * support for Element.matches - currently supported in all 
 * up to date browsers.
 * @param selector: Query for matching element
 */
Element.prototype.polyclosest = function(selector) {
    var node = this;
    while (node) {
        if (node.matches(selector)) {
            return node;
        } else {
            node = node.parentElement;
        }
    }
    return null;
}

/**
 * polyempty: Remove all descendents of a node
 */
Element.prototype.polyempty = function() {
    while (this.lastChild) {
        this.removeChild(this.lastChild);
    }
}

/**
 * polyfetch: A usable-enough implementation of the coming fetch API
 * @param url:          Request URL
 * @optional options:   Options object (keys: [method, headers, body])
 */
window.polyfetch = function(url, options) {
    var FORBIDDEN_HEADERS = [
        'accept-charset', 'accept-encoding',
        'access-control-request-headers',
        'access-control-request-method',
        'connection', 'content-length',
        'cookie', 'cookie2', 'date', 'dnt',
        'expect', 'host', 'keep-alive', 'referer',
        'te', 'trailer', 'transer-encoding',
        'upgrade', 'user-agent', 'via'
    ];
    var xmlhttp = new XMLHttpRequest();
    var key;
    
    options = (options) ? options : {};

    return new Promise(function (resolve, reject) {
        xmlhttp.onload = function () {
            
            //FIXME: This is non-conformant with the fetch API standard.
            if (xmlhttp.status === 200) {
                resolve(xmlhttp.response);
            } else {
                reject(new Error(xmlhttp.statusText));
            }
        }

        xmlhttp.onerror = function () {
            reject(new Error('Network Error'));            
        }

        xmlhttp.open(options.method || 'GET', url, true);

        for (key in options.headers) {
            if (!(key.toLowerCase() in FORBIDDEN_HEADERS)) {
                xmlhttp.setRequestHeader(key, options.headers[key]);
            }
        }

        xmlhttp.send(options.body);
    });
}
