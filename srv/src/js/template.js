/* 
 * Filename:    template.js
 * Author:      Harrison Hubbell
 * Date:        08/12/2015
 * Description: Frontend templating engine.
 */

/**
 * Template: Manage creation of html.
 */
function Template() {}
Template.prototype.HUD = 'hud';
Template.prototype.TAP = 'tap';

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
 * Template.wrappers: Make wrappers for hud and beer views
 * @param kegs:    beers to wrap
 * @return:         string
 */
Template.prototype.wrappers = function (kegs) {
    return this.beerViewWrapper(kegs) + this.hudWrapper();
}

/**
 * Template.hudWrapper: Create wrapper for hud
 * @return:         string
 */
Template.prototype.hudWrapper = function () {
    return "<section id='" + this.HUD + "'></section>";
}

/**
 * Template.hud: Render the hud content
 * @param kegs:     Array of kegs to render
 */
Template.prototype.hud = function (kegs) {
    var target = document.getElementById(this.HUD);
    var content = [];

    for (var i = 0; i < kegs.length; i++) {
        content.push("<a href='#tap" + (i + 1) + "' class='beer-link'>" +
            this.remaining(
                kegs[i].remaining,            
                "<h4>" + kegs[i].name + "</h4>"
            ) + "</a>"
        );
    }

    target.innerHTML = content.join('');
}

/**
 * Template.nav: Render navigation
 * @param kegs:     kegs to put in nav
 * @return:         string
 */
Template.prototype.nav = function (kegs) {
    var content = [];

    for (var i = 0; i < kegs.length; i++) {
        content.push("<a href='#tap" + (i + 1) + "'>" + kegs[i].name + "</a>");
    }

    return content.join('');
}

/**
 * Template.consumption: Render beer consumption graph
 * @param values:   (x, y) value array
 * @option title:   optional title for box
 * @option display: optional method to display (scatter[default], bar, both)
 */
Template.prototype.consumption = function (values, title, plot) {
    var opt = {class: 'chart'};
    var plot;
    var graph;

    title = title || 'Consumption';

    switch (plot) {
        case 'bar':
            plot = new BarGraph(values.map(function (el) { return el[1] }));
            graph = plot.renderTemplate();
            break;
        case 'both':
            plot = new BarGraph(values.map(function (el) { return el[1] }));
            graph = plot.renderInner();
            plot = new ScatterPlot(values);
            graph += plot.renderInner();
            graph = "<svg>" + graph + "</svg>";
            break;
        default:
            plot = new ScatterPlot(values);
            graph = plot.renderTemplate();
            break;
    }

    return this.contentBox(title, graph, opt);
}

/**
 * Template.info: Render beer info content box
 * @param kv:       key, value object of beer
 * @option title:   optional title for box
 * @return:         string
 */
Template.prototype.info = function (kv, title) {
    var DISPLAY = ['Name', 'Brand', 'ABV', 'IBU', 'Rating']
    var content = [];

    title = title || 'Beer Info';

    for (var i = 0; i < DISPLAY.length; i++) {     
        content.push("<div class='serving-data'><span class='serving-attribute'>" + DISPLAY[i] + ": </span><span class='serving-content'>" + kv[DISPLAY[i].toLowerCase()] + "</span></div>");
    }

    return this.contentBox(title, content.join(''));
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
 */
Template.prototype.beerView = function (beer, i, arr) {
    var target = document.getElementById(this.TAP + (i + 1));
    var beerInfo = this.info(beer, 'Now Serving on Tap ' + (i + 1));
    var beerRem = this.remaining(beer.remaining);
    var beerAdv = this.consumption(beer.consumption);

    target.innerHTML = "<section class='beer-hud'>" + beerInfo +
                beerRem + "</section>" + beerAdv + "</section>";

}

/**
 * Template.beerView: Render a beer view wrapper
 * @param kegs:     array of kegs to create wrappers for
 * @return:         string
 */
Template.prototype.beerViewWrapper = function (kegs) {
    return kegs.map(function (beer, i, arr) {
        return "<section id='" + this.TAP + (i + 1) + "' class='beer-view'></section>";
    }, this).join('');
}

/**
 * Template.beerViewAll: Render all beer views
 * @param kegs:     array of kegs to render
 */
Template.prototype.beerViewAll = function (kegs) {
    kegs.map(this.beerView, this);
}
