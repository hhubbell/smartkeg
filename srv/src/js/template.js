/* 
 * Filename:    template.js
 * Author:      Harrison Hubbell
 * Date:        08/12/2015
 * Description: Frontend templating engine.
 */

/**
 * Template: Manage creating of html.
 */
function Template() {}

/**
 * Template.fragmentFromString: Create a Document Fragment from HTML string.
 * NOTE: This is experimental and not fully supported.
 * @param html: html string
 * @return      documentFragment
 */
Template.prototype.fragmentFromString = function (html) {
    return document.createRange().createContextualFragment(html);
}

/**
 * Template.contentBox: Basic wireframe for a "content box" element.
 * @param header:   content box header (rich or string)
 * @option content: content box conttent (rich or string)
 * @option options: classes, ids, etc.
 * @return:         string
 */
Template.prototype.contentBox = function (header, content, options) {
    var fmt;
    var wclass = '';
    var wid = '';
    var cclass = '';
    var cid = '';

    content = content || '';
    
    if (options) {
        wclass = (options.class) ? options.class : wclass;
        wid = (options.id) ? "id='" + options.id + "'" : wid;
        cclass = (options.contentClass) ? options.contentClass : cclass;
        cid = (options.contentId) ? "id='" + options.contentId + "'" : cid;
    }

    return "<section class='content-box " + wclass + "' " + wid + ">" +
        "<header class='content-header'>" + 
        header +
        "</header>" +
        "<section class='content-area " + cclass + "' " + cid + ">" +
        content +
        "</section></section>"
}

/**
 * Template.hud: Render the hud content
 * @param kegs:     Array of kegs to render
 * @return:         string
 */
Template.prototype.hud = function (kegs) {
    var content = [];

    for (var i = 0; i < kegs.length; i++) {
        content.push("<a href='#tap" + (i + 1) + "' class='beer-link'>" +
            this.remaining(
                kegs[i].remaining,            
                kegs[i].name
            ) + "</a>"
        );
    }

    return content.join('')
}

/**
 * Template.remaining: Render a remaining graph content box
 * @param amount:   value to graph (between 0 and 1)
 * @option title:   optional value to title box.
 * @return:         string
 */
Template.prototype.remaining = function (amount, title) {
    title = title || 'Amount Remaining';

    return this.contentBox(title, new RemainingGraph(amount).renderTemplate());
}

/**
 * Template.beerView: Render a single advanced beer view
 * @param beer:     single keg object
 * @param i:        array index
 * @param arr:      array
 * @return:         string
 */
Template.prototype.beerView = function (beer, i, arr) {
    var beerInfo = this.contentBox(beer.name, 'Beer info goes here');
    var beerRem = this.remaining(beer.remaining);
    var beerAdv = this.contentBox('Consumption', 'Advanced consumption graph will go here');
    var content = [beerInfo, beerRem, beerAdv];

    return "<section id='tap" + (i + 1) + "' class='beer-view'>" + content.join('') + "</section>";
}

/**
 * Template.beerViewAll: Render all beer views
 * @param kegs:     Array of kegs to render
 * @return:         string
 */
Template.prototype.beerViewAll = function (kegs) {
    return kegs.map(this.beerView, this).join('');
}
