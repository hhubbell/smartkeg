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

ScatterPlot.prototype.render_points = function(bottom) {
    var self = this;

    this.sets.forEach(function(set) {
        var radius = self.radius;
        var style = self.style;
        var length = set[set.length - 1].x;
 
        for (var i = 0; i < set.length; i++) {
            var y_prog = set[i].y;
            var j = i - 1;
            
            while (set[j]) {
                y_prog += set[j].y;
                j -= 1;
            }

            var y_val = y_prog / bottom * self.height;

            //var y_val = self.height - (set[i].y - (set[i-1] ? self.height - set[i-1].y : 0));
            var x_val = ((set[i].x / length) * self.width) //+ ((self.width / length) / 2);
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

        console.log(bottom, start_percent, width_percent, set)
    
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

ScatterPlot.prototype.render = function(max, points, trend) {
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;

    if (trend) this.render_seasonal_trendline(max);
    if (points) this.render_points(max);
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
    this.height = this.element.clientHeight;
    this.width = this.element.clientWidth;

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
        text.textContent = (this.categories[i] * 100).toFixed(2) + '%';

        this.element.appendChild(rect);
        this.element.appendChild(text);
    }
}
