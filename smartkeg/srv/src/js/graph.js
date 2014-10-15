/* ------------------------------------------------------------------------ *
 * Filename:    graph.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Manage formatting SVG graphs
 * ------------------------------------------------------------------------ */

function Graph(selector) {
    this.element = document.querySelector(selector);
    this.sets = [];
}

Graph.prototype.add_set = function(set_obj) {
    this.sets.push(set_obj);
}

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

Graph.prototype.render_means = function() {
    var self = this;
    this.sets.forEach(function(set) {
        var radius = set.radius;    
        var style = set.style;
        
        for (x in set.x) {
            var mean = set.x[x].mean;
            var point = document.createElementNS('http://www.w3.org/2000/svg', style);

            point.classList.add('chart-day-mean');
            
            if (style === 'rect') {
                point.setAttributeNS(null, 'x', x - radius/2);
                point.setAttributeNS(null, 'y', mean - radius/2);
                point.setAttributeNS(null, 'width', radius);
                point.setAttributeNS(null, 'height', radius);
            } else if (style === 'circle') {
                point.setAttributeNS(null, 'cx', x);
                point.setAttributeNS(null, 'cy', mean);
                point.setAttributeNS(null, 'r', radius);
            }

            self.element.appendChild(point);
        }
    });

}

Graph.prototype.render_sets = function() {
    var self = this;
    
    this.sets.forEach(function(set) {
        var radius = set.radius;    
        var style = set.style;
        
        for (x in set.x) {
            set.x[x].y.forEach(function(y) {
                var point = document.createElementNS('http://www.w3.org/2000/svg', style);
        
                point.classList.add('chart-day');
        
                if (style === 'rect') {
                    point.setAttributeNS(null, 'x', x - radius/2);
                    point.setAttributeNS(null, 'y', y - radius/2);
                    point.setAttributeNS(null, 'width', radius);
                    point.setAttributeNS(null, 'height', radius);
                } else if (style === 'circle') {
                    point.setAttributeNS(null, 'cx', x);
                    point.setAttributeNS(null, 'cy', y);
                    point.setAttributeNS(null, 'r', radius);
                }
                self.element.appendChild(point);            
            });
        }
    });
}

Graph.prototype.render_seasonal_trendline = function() {
    var self = this;
    var line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    var line_string = '';

    this.sets.forEach(function(set) {
        for (x in set.x) {
            var y = set.x[x].mean;

            line_string += x + ',' + y + ' ';
        }

        line.classList.add('chart-trendline');
        line.setAttributeNS(null, 'points', line_string);
        self.element.appendChild(line);
    });
}
