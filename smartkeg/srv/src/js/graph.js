/* ------------------------------------------------------------------------ *
 * Filename:    graph.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Manage formatting SVG graphs.
 * ------------------------------------------------------------------------ */

function ScatterPlot(selector) {
    this.set_canvas(selector);
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;
    this.sets = [];
}

ScatterPlot.prototype.set_canvas = function(selector) {
    this.element = document.querySelector(selector);
    this.defs = this.element.getElementsByTagNameNS('http://www.w3.org/2000/svg', 'defs')[0];
    if (!this.defs) {
        this.defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        this.element.appendChild(this.defs);
    }
}

ScatterPlot.prototype.set_independent_variable = function(key) {
    this.independent_variable = key;
}

ScatterPlot.prototype.set_point_radius = function(radius) {
    this.radius = radius;
}

ScatterPlot.prototype.add_set = function(set_obj) {
    this.sets.push(set_obj);
}

ScatterPlot.prototype.calculate_means = function() {
    var self = this;
    this.sets.forEach(function(set) {
        for (x in set[self.independent_variable]) {
            var y = set[self.independent_variable][x].y;
            var sum = 0;

            y.forEach(function(point) {
                sum += point;
            });

            set.x[x].mean = sum / y.length;
        }
    });
}

ScatterPlot.prototype.render_means = function() {
    var self = this;
    this.sets.forEach(function(set) {
        var radius = self.radius;
        var style = set.style;
        var length = set[self.independent_variable].length;

        for (x in set[self.independent_variable]) {
            var y_val = self.height - set[self.independent_variable][x].mean;
            var x_val = ((x / length) * self.width) + ((self.width / length) / 2);
            var point = document.createElementNS('http://www.w3.org/2000/svg', style);

            point.classList.add('chart-day-mean');

            if (style === 'rect') {
                point.setAttributeNS(null, 'x', x_val - radius/2);
                point.setAttributeNS(null, 'y', y_val - radius/2);
                point.setAttributeNS(null, 'width', radius);
                point.setAttributeNS(null, 'height', radius);
            } else if (style === 'circle') {
                point.setAttributeNS(null, 'cx', x_val);
                point.setAttributeNS(null, 'cy', y_val);
                point.setAttributeNS(null, 'r', radius);
            }

            self.element.appendChild(point);
        }
    });

}

ScatterPlot.prototype.render_sets = function() {
    var self = this;

    this.sets.forEach(function(set) {
        var radius = self.radius;
        var style = set.style;        
        var length = set[self.independent_variable].length;

        for (x in set[self.independent_variable]) {
            var x_val = ((x / length) * self.width) + ((self.width / length) / 2);

            set[this.independent_variable][x].y.forEach(function(y) {
                var y_val = self.height - y;
                var point = document.createElementNS('http://www.w3.org/2000/svg', style);

                point.classList.add('chart-day');

                if (style === 'rect') {
                    point.setAttributeNS(null, 'x', x_val - radius/2);
                    point.setAttributeNS(null, 'y', y_val - radius/2);
                    point.setAttributeNS(null, 'width', radius);
                    point.setAttributeNS(null, 'height', radius);
                } else if (style === 'circle') {
                    point.setAttributeNS(null, 'cx', x_val);
                    point.setAttributeNS(null, 'cy', y_val);
                    point.setAttributeNS(null, 'r', radius);
                }
                self.element.appendChild(point);
            });
        }
    });
}

ScatterPlot.prototype.render_seasonal_trendline = function(gradient) {
    var self = this;
    var line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    var line_string = '';

    for (var i = 0; i < this.sets.length; i++) {
        var set = this.sets[i];
        var length = set[this.independent_variable].length

        for (x in set[this.independent_variable]) {
            var y_val = this.height - set[this.independent_variable][x].mean;
            var x_val = ((x / length) * self.width) + ((self.width / length) / 2);
            line_string += x_val + ',' + y_val + ' ';
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

ScatterPlot.prototype.render = function(set, mean, trend, gradient) {
    if (set) this.render_sets();
    if (trend) this.render_seasonal_trendline();
    if (mean) this.render_means();
    if (gradient) this.render_seasonal_trendline(gradient);    
}


function BarGraph(selector) {
    this.set_canvas(selector);
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;
    this.categories = []
}

BarGraph.prototype.set_canvas = function(selector) {
    this.element = document.querySelector(selector);
    this.defs = this.element.getElementsByTagNameNS('http://www.w3.org/2000/svg', 'defs')[0];
    if (!this.defs) {
        this.defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        this.element.appendChild(this.defs);
    }
}

BarGraph.prototype.add_category = function(category) {
    this.categories.push(category);
}

BarGraph.prototype.render = function() {
    var bar_width = (100 / this.categories.length || 1) + "%";
    var bar_x = this.width / this.categories.length;
    
    for (var i = 0; i < this.categories.length; i++) {
        var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        
        var bar_top = (1 - (this.categories[i].value)) * this.height

        rect.classList.add('remaining-bar');
        
        rect.setAttributeNS(null, 'x', bar_x * i);
        rect.setAttributeNS(null, 'y', bar_top);
        rect.setAttributeNS(null, 'width', bar_width);
        rect.setAttributeNS(null, 'height', this.height - bar_top);
        this.element.appendChild(rect);
    }
}
