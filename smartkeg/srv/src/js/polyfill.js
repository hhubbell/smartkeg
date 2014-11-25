/* ------------------------------------------------------------------------ *
 * Filename:    polyfill.js
 * Author:      Harrison Hubbell
 * Date:        11/24/2014
 * Description: Polyfills for needed  functionality
 * ------------------------------------------------------------------------ */
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

Element.prototype.polyempty = function() {
    while (this.lastChild) {
        this.removeChild(this.lastChild);
    }
}

