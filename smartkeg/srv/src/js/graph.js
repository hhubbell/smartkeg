/* ------------------------------------------------------------------------ *
 * Filename:    graph.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Manage formatting SVG graphs.
 * ------------------------------------------------------------------------ */

function ScatterPlot(selector) {
    this.SVG_NS = 'http://www.w3.org/2000/svg';
    this.set_canvas(selector);
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;
    this.selector = selector;
    this.sets = [];
}

ScatterPlot.prototype.push = function(set) {
    this.sets.push(set);
}

ScatterPlot.prototype.pop = function() {
    this.sets.pop();
}

ScatterPlot.prototype.popall = function() {
    this.sets.length = 0;
}

ScatterPlot.prototype.clear = function() {
    this.element.polyempty();
    this.set_defs();
}

ScatterPlot.prototype.set_canvas = function(selector) {
    this.element = document.querySelector(selector);
    this.set_defs();
}

ScatterPlot.prototype.set_defs = function() {
    this.defs = this.element.getElementsByTagNameNS(this.SVG_NS, 'defs')[0];

    if (!this.defs) {
        this.defs = document.createElementNS(this.SVG_NS, 'defs');
        this.element.appendChild(this.defs);
    }
}

ScatterPlot.prototype.set_radius = function(radius) {
    this.radius = radius;
}

ScatterPlot.prototype.set_style = function(style) {
    this.style = style;
}

ScatterPlot.prototype.render_points = function() {
    var self = this;

    this.sets.forEach(function(set) {
        var radius = self.radius;
        var style = self.style;
        var length = set.length;

        for (x in set) {
            var y_val = self.height - set[x];
            var x_val = ((x / length) * self.width) + ((self.width / length) / 2);
            var point = document.createElementNS(self.SVG_NS, style);

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

ScatterPlot.prototype.render_seasonal_trendline = function(gradient) {
    var self = this;
    var line = document.createElementNS(this.SVG_NS, 'polyline');
    var line_string = '';

    for (var i = 0; i < this.sets.length; i++) {
        var set = this.sets[i];
        var length = set.length

        for (x in set) {
            var y_val = this.height - set[x];
            var x_val = ((x / length) * self.width) + ((self.width / length) / 2);
            line_string += x_val + ',' + y_val + ' ';
        }

        line.classList.add('chart-trendline');

        if (gradient) {
            var gradient = document.createElementNS(this.SVG_NS, 'linearGradient');
            var start = document.createElementNS(this.SVG_NS, 'stop');
            var stop = document.createElementNS(this.SVG_NS, 'stop');

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

ScatterPlot.prototype.render = function(points, trend) {
    if (trend) this.render_seasonal_trendline();
    if (points) this.render_points();
}


function BarGraph(selector) {
    this.SVG_NS = 'http://www.w3.org/2000/svg';
    this.REM_MED = .45;
    this.REM_LOW = .20;
    this.set_canvas(selector);
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;
    this.categories = []
}

BarGraph.prototype.push = function(category) {
    this.categories.push(category);
}

BarGraph.prototype.pop = function() {
    this.categories.pop();
}

BarGraph.prototype.popall = function() {
    this.categories.length = 0;
}

BarGraph.prototype.clear = function() {
    this.element.polyempty();
    this.set_defs();
}

BarGraph.prototype.set_canvas = function(selector) {
    this.element = document.querySelector(selector);
    this.set_defs()
}

BarGraph.prototype.set_defs = function() {
    this.defs = this.element.getElementsByTagNameNS(this.SVG_NS, 'defs')[0];

    if (!this.defs) {
        this.defs = document.createElementNS(this.SVG_NS, 'defs');
        this.element.appendChild(this.defs);
    }
}

BarGraph.prototype.render = function() {
    var bar_width = (100 / this.categories.length || 1) + "%";
    var bar_x = this.width / this.categories.length;
    var TEXT_WIDTH = 124;

    for (var i = 0; i < this.categories.length; i++) {
        var rect = document.createElementNS(this.SVG_NS, 'rect');
        var text = document.createElementNS(this.SVG_NS, 'text');
        var bar_top = (1 - this.categories[i]) * this.height

        // ASSIGN COLOR BASED ON AMOUNT REMAINING
        if (this.categories[i] < this.REM_LOW) {
            rect.classList.add('low');
        } else if (this.categories[i] < this.REM_MED) {
            rect.classList.add('medium');
        } else {
            rect.classList.add('ok');
        }
        
        rect.setAttributeNS(null, 'x', bar_x * i);
        rect.setAttributeNS(null, 'y', bar_top);
        rect.setAttributeNS(null, 'width', bar_width);
        rect.setAttributeNS(null, 'height', this.height - bar_top);

        
        text.classList.add('remaining-text');
        text.setAttributeNS(null, 'x', this.width / 2 - TEXT_WIDTH / 2);
        text.setAttributeNS(null, 'y', this.height / 2);
        text.textContent = this.categories[i] * 100 + '%';

        this.element.appendChild(rect);
        this.element.appendChild(text);
    }
}
