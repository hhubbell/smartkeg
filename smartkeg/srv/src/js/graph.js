/* ------------------------------------------------------------------------ *
 * Filename:    graph.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Manage formatting SVG graphs.
 * ------------------------------------------------------------------------ */

/**
 * ScatterPlot Object is responsible for rendering scatterplots on SVG
 * @param selector: A selector that defines the SVG
 */
function ScatterPlot(selector) {
    this.set_canvas(selector);
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;
    this.sets = [];
}

/**
 * Initialize the SVG area for graphing and define a <defs> child.
 * @param selector: A selector that defines the SVG
 */
ScatterPlot.prototype.set_canvas = function(selector) {
    this.element = document.querySelector(selector);
    this.defs = this.element.getElementsByTagNameNS('http://www.w3.org/2000/svg', 'defs')[0];
    if (!this.defs) {
        this.defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        this.element.appendChild(this.defs);
    }
}

/**
 * Add a set.
 * @param set_obj: A set Object.
 */
ScatterPlot.prototype.add_set = function(set_obj) {
    this.sets.push(set_obj);
}

/**
 * Calculate y mean if it does not exist for x values of sets.
 */
ScatterPlot.prototype.calculate_means = function() {
    this.sets.forEach(function(set) {
        for (x in set.x) {
            var y = set.x[x].y;
            var sum = 0;

            y.forEach(function(point) {
                sum += point;
            });

            set.x[x].mean = sum / y.length;
        }
    });
}

/**
 * Draw means on graph.
 */
ScatterPlot.prototype.render_means = function() {
    var self = this;
    this.sets.forEach(function(set) {
        var radius = set.radius;
        var style = set.style;

        for (x in set.x) {
            var value = self.height - set.x[x].mean;
            var point = document.createElementNS('http://www.w3.org/2000/svg', style);

            point.classList.add('chart-day-mean');

            if (style === 'rect') {
                point.setAttributeNS(null, 'x', x - radius/2);
                point.setAttributeNS(null, 'y', value - radius/2);
                point.setAttributeNS(null, 'width', radius);
                point.setAttributeNS(null, 'height', radius);
            } else if (style === 'circle') {
                point.setAttributeNS(null, 'cx', x);
                point.setAttributeNS(null, 'cy', value);
                point.setAttributeNS(null, 'r', radius);
            }

            self.element.appendChild(point);
        }
    });

}

/**
 * Draw all sets on the graph.
 */
ScatterPlot.prototype.render_sets = function() {
    var self = this;

    this.sets.forEach(function(set) {
        var radius = set.radius;
        var style = set.style;

        for (x in set.x) {
            set.x[x].y.forEach(function(y) {
                var value = self.height - y;
                var point = document.createElementNS('http://www.w3.org/2000/svg', style);

                point.classList.add('chart-day');

                if (style === 'rect') {
                    point.setAttributeNS(null, 'x', x - radius/2);
                    point.setAttributeNS(null, 'y', value - radius/2);
                    point.setAttributeNS(null, 'width', radius);
                    point.setAttributeNS(null, 'height', radius);
                } else if (style === 'circle') {
                    point.setAttributeNS(null, 'cx', x);
                    point.setAttributeNS(null, 'cy', value);
                    point.setAttributeNS(null, 'r', radius);
                }
                self.element.appendChild(point);
            });
        }
    });
}

/**
 * Draw the seasonal trendline on the graph.
 * @param gradient [optional]: Draws a gradient below the line if true.
 */
ScatterPlot.prototype.render_seasonal_trendline = function(gradient) {
    var line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    var line_string = '';

    for (var i = 0; i < this.sets.length; i++) {
        var set = this.sets[i];

        for (x in set.x) {
            var value = this.height - set.x[x].mean;
            line_string += x + ',' + value + ' ';
        }

        line.classList.add('chart-trendline');

        if (gradient) {
            var gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
            var start = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            var stop = document.createElementNS('http://www.w3.org/2000/svg', 'stop');

            start.classList.add('chart-fillunder-start');
            start.setAttributeNS(null, 'offset', '0%');

            stop.classList.add('chart-fillunder-stop');
            stop.setAttributeNS(null, 'offset', '100%');

            gradient.setAttributeNS(null, 'id', 'chart-fillunder');
            gradient.setAttributeNS(null, 'x1', '0%');
            gradient.setAttributeNS(null, 'y1', '0%');
            gradient.setAttributeNS(null, 'x2', '100%');
            gradient.setAttributeNS(null, 'y2', '100%');
            gradient.appendChild(start);
            gradient.appendChild(stop);

            this.defs.appendChild(gradient);

            line.classList.add('chart-trendline-fill');            
            line.setAttributeNS(null, 'fill', 'url(#chart-fillunder)');
        } else {
            line.classList.add('chart-trendline-nofill');
        }

        line.setAttributeNS(null, 'points', line_string);
        this.element.appendChild(line);
    }
}

/**
 * Render is a wrapper to apply subrender routines with one function call.
 * All parameters are optional.
 * @param set: Render set points if true.
 * @param mean: Render mean points if true.
 * @param trend: Render trendline if true.
 * @param gradient: Render a trendline gradient if true.
 */
ScatterPlot.prototype.render = function(set, mean, trend, gradient) {
    if (gradient) this.render_seasonal_trendline(gradient);
    if (set) this.render_sets();
    if (trend) this.render_seasonal_trendline();
    if (mean) this.render_means();
}


/**
 * BarGraph Object is responsible for rendering bar graphs on SVG
 */
function BarGraph(selector) {
    this.set_canvas(selector);
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;
    this.categories = []
}

/**
 * Initialize the SVG area for graphing and define a <defs> child.
 * @param selector: A selector that defines the SVG
 */
BarGraph.prototype.set_canvas = function(selector) {
    this.element = document.querySelector(selector);
    this.defs = this.element.getElementsByTagNameNS('http://www.w3.org/2000/svg', 'defs')[0];
    if (!this.defs) {
        this.defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        this.element.appendChild(this.defs);
    }
}

/**
 * Add a category.
 * @param category: A category Object.
 */
BarGraph.prototype.add_category = function(category) {
    this.categories.push(category);
}

/**
 * Render the Bar Chart.
 */
BarGraph.prototype.render = function() {
    var bar_width = this.width / this.categories.length;
    
    for (var i = 0; i < this.categories.length; i++) {
        var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        
        var bar_top = (1 - (this.categories[i].y / 100)) * this.height

        rect.classList.add('remaining-bar');
        
        rect.setAttributeNS(null, 'x', bar_width * i);
        rect.setAttributeNS(null, 'y', bar_top);
        rect.setAttributeNS(null, 'width', bar_width);
        rect.setAttributeNS(null, 'height', this.height - bar_top);
        this.element.appendChild(rect);
    }
}
