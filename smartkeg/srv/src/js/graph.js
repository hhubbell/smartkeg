/* ------------------------------------------------------------------------ *
 * Filename:    graph.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Manage formatting SVG graphs
 * ------------------------------------------------------------------------ */

function Graph(selector) {
    this.element = document.querySelector(selector);
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;
    this.sets = [];
}

/**
 * Add a set.
 */
Graph.prototype.add_set = function(set_obj) {
    this.sets.push(set_obj);
}

/**
 * Calculate y mean if it does not exist for x values of sets.
 */
Graph.prototype.calculate_means = function() {
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
Graph.prototype.render_means = function() {
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
Graph.prototype.render_sets = function() {
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
Graph.prototype.render_seasonal_trendline = function(gradient) {
    var self = this;
    var line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    var line_string = '';

    for (var i = 0; i < this.sets.length; i++) {
        var set = this.sets[i];

        for (x in set.x) {
            var value = self.height - set.x[x].mean;

            line_string += x + ',' + value + ' ';
        }

        line.classList.add('chart-trendline');

        if (gradient) {
            var defs = this.element.getElementsByTagNameNS('http://www.w3.org/2000/svg', 'defs')[0];
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

            defs.appendChild(gradient);

            line.setAttributeNS(null, 'fill', 'url(#chart-fillunder)');
        } else {
            line.classList.add('chart-trendline-nofill');
        }

        line.setAttributeNS(null, 'points', line_string);
        self.element.appendChild(line);
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
Graph.prototype.render = function(set, mean, trend, gradient) {
    var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    this.element.appendChild(defs);

    if (gradient) {
        this.render_seasonal_trendline(gradient);
    }

    if (set) {
        this.render_sets();
    }

    if (trend) {
        this.render_seasonal_trendline();
    }

    if (mean) {
        this.render_means();
    }
}
