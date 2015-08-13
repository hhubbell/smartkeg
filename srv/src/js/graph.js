/* 
 * Filename:    graph.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Manage formatting SVG graphs.
 */

/**
 * Graph: Parent Class for all SVG graph Objects.
 * @option values:  An array of values to graph (Children must decide how).
 *                  Values are optional and can be added later.
 */
function Plot(values) {
    this.values = [];
    
    if (values) {
        this.push(values);
    }
}
Plot.prototype.SVGNAMESPACE = 'http://www.w3.org/2000/svg';

/**
 * Plot.push: Add a set of values to graph
 * @param values:   Values to append.
 */
Plot.prototype.push = function (values) {
    this.values.push(values);
}

/**
 * Plot.pop: Remove a set of values
 */
Plot.prototype.pop = function () {
    this.values.pop();
}

/**
 * Plot.popall: Remove all sets of values
 */
Plot.prototype.popall = function() {
    this.values.length = 0;
}

/**
 * Plot.renderTo: Render to a specified element.
 * @param element: element to render to.
 */
Plot.prototype.renderTo = function (element) {
    element.innerHTML = this.renderTemplate();
}

/**
 * Plot.renderInner: Render the inner parts of the svg graph
 * @return:         string
 */
Plot.prototype.renderInner = function () {
    return;
}

/**
 * Plot.renderTemplate: Return a string representation of the svg.
 * @return:         string
 */
Plot.prototype.renderTemplate = function () {
    return '<svg>' + this.renderInner() + '</svg>';
}


/**
 * ScatterPlot: Class for making 2D scatter plots (x, y)
 * @option values:  Array of values (x,y).
 */
function ScatterPlot(values, radius, style) {
    Plot.call(this, values);
    
    this.radius = radius;
    this.style = style;
}
ScatterPlot.prototype = Object.create(Plot.prototype);
ScatterPlot.prototype.constructor = ScatterPlot;

/**
 * ScatterPlot.renderTemplate: Return a string representation of the svg.
 * @param height:   graph height
 * @param width:    graph width
 * @return:         string
 * 
 * XXX FIXME: This will not render like other graphs -- use percents
 */
ScatterPlot.prototype.renderInner = function (height, width) {
    var self = this;
    var parent = document.querySelector(selector);
    var height = parent.clientHeight;
    var width = parent.clientWidth;
    var element = [];
    var ptOpt = {class: 'chart-day-mean'}
    var point;
    var x;
    var y;
    
    this.values.forEach(function (set) {
        for (var i = 0; i < set.length; i++) {
            x = set[i][0] / 100 * width;
            y = set[i][1] / 100 * height;
            element.push(this.pointTemplate(x, y, self.style, self.radius, ptOpt));
        }
    });

    return element.join('');
}

/**
 * ScatterPlot.pointFragment: Create a string of an svg point
 * @param x:        x value
 * @param y:        y value
 * @param type:     point type (circle or rect)
 * @param size:     point size
 * @param options:  point options
 * @return          string
 */
ScatterPlot.prototype.pointTemplate = function (x, y, type, size, options) {
    var point;
    var pcl = '';

    if (options && options.class) {
        pcl = "class='" + options.class + "'";  
    }

    switch (type) {
        case 'rect':
            point = "<rect x='" + x + "' y='" + y + "' width='" + size + "' height='" + size + "'  " + pcl + "></rect>";
            break;
        case 'circle':
            point = "<circle cx='" + x + "' cy='" + y + "' r='" + size + "' " + pcl + "></circle>";
            break;
    }

    return point;
}

/*
 * XXX FIXME: Make this work!
ScatterPlot.prototype.render_seasonal_trendline = function(bottom, vertical_fix, start_percent, width_percent, set, type) {
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;
    
    var line = document.createElementNS(this.SVG_NS, 'polyline');
    if (type == 'values') {
        var line_string = '0,0 ';
    } else {
        var line_string = '';
    }
    var start = start_percent * this.width;
    var length = set[set.length - 1].x || 1;

    for (var i = 0; i < set.length; i++) { 
        var y_prog = set[i].y;
        var j = i - 1;
            
        while (set[j]) {
            y_prog += set[j].y;
            j -= 1;
        }

        var y_val = vertical_fix + (y_prog / bottom * this.height);
        var x_val = start + (set[i].x / length) * (width_percent * this.width);
        line_string += x_val + ',' + y_val + ' ';
    }

    if (type == 'values') {
        line.classList.add('chart-trendline');
    } else if (type == 'prediction') {
        line.classList.add('chart-prediction');
    }
    
    line.setAttributeNS(null, 'points', line_string);
        
    this.element.appendChild(line);

    return y_val
}
*/


/**
 * BarGraph: Class for making bar graphs
 * @option  values: Array of y values
 */
function BarGraph(values) {
    Plot.call(this, values);
}
BarGraph.prototype = Object.create(Plot.prototype);
BarGraph.prototype.constructor = BarGraph;

/**
 * BarGraph.renderInner: Return a string representation of the svg innards.
 * @return:         string
 */
BarGraph.prototype.renderInner = function () {
    var max = Math.max.apply(null, this.values);
    var content = [];
    var barWidth = (100 / this.values.length || 1);
    var barHeight;
    var x;
    var y;

    for (var i = 0; i < this.values.length; i++) {
        barHeight = (this.values[i] / max * 100);
        y = 100 - barHeight;
        x = barWidth * i;
        content.push("<rect x='" + x + "%' y='" + y + "%' width='" + barWidth + "%' height='" + barHeight + "%'></rect>");
        
    }

    return content.join('');
}


/**
 * RemainingGraph: Class for making remaining graphs
 * @option value: single y value (between 0 and 1)
 */
function RemainingGraph (value) {
    Plot.call(this, value);
}
RemainingGraph.prototype = Object.create(Plot.prototype);
RemainingGraph.prototype.constructor = RemainingGraph;
RemainingGraph.prototype.REMAININGMEDIUM = .45;
RemainingGraph.prototype.REMAININGLOW = .20;

/**
 * RemainingGraph.push: Override normal push so RemainingGraph can only hold a single value
 */
RemainingGraph.prototype.push = function (val) {
    this.values = val;
    this.value = this.values;
}

/**
 * RemainingGraph.renderInner: Render the remaining bar and text percent.
 * @return:         string
 */
RemainingGraph.prototype.renderInner = function () {
    var barHeight = (this.value * 100).toFixed(2);
    var y = 100 - barHeight;
    var textClass = "class='remaining-text'";
    var remClass;    

    if (this.value < this.REMAININGLOW) {
        remClass = "class='low'";
    } else if (this.value < this.REMAININGMEDIUM) {
        remClass = "class='medium'";
    } else {
        remClass = "class='ok'";
    }

    return "<rect x='0' y='" + y + "%' width='100%' height='" +
        barHeight + "%' " + remClass + "></rect>" +
        "<text x='50%' y='50%' " + textClass + ">" + barHeight + "%</text>";
}
