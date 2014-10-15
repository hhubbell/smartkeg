/* ------------------------------------------------------------------------ *
 * Filename:    graph.js
 * Author:      Harrison Hubbell
 * Date:        10/14/2014
 * Description: Manage formatting SVG graphs
 * ------------------------------------------------------------------------ */

function Graph(selector) {
    this.element = document.querySelector(selector);
    this.points = {'x':{}};
    this.means = {'x':{}};
}

Graph.prototype.add_point = function(point_obj) {
    this.points.x[point_obj.x] = this.points.x[point_obj.x] ? this.points.x[point_obj.x] : [];
    this.points.x[point_obj.x].push(point_obj);
}

Graph.prototype.calculate_means = function() {
    for (x in this.points.x) {
        var sum = 0;

        this.points.x[x].forEach(function(pt) {
            sum += pt.y;
        });

        this.means.x[x] = sum / this.points.x[x].length;
    }
}

Graph.prototype.render_means = function(style, radius) {
    for (x in this.means.x) {
        var y = this.means.x[x]
        var point = document.createElementNS('http://www.w3.org/2000/svg', style);
        
        point.classList.add('chart-day-mean');
        
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

        this.element.appendChild(point);
    }
}

Graph.prototype.render_points = function() {
    var self = this;

    for (x in this.points.x) {
        this.points.x[x].forEach(function(pt) {
            var point = document.createElementNS('http://www.w3.org/2000/svg', pt.style);
        
            point.classList.add('chart-day');
        
            if (pt.style === 'rect') {
                point.setAttributeNS(null, 'x', pt.x - pt.radius/2);
                point.setAttributeNS(null, 'y', pt.y - pt.radius/2);
                point.setAttributeNS(null, 'width', pt.radius);
                point.setAttributeNS(null, 'height', pt.radius);
            } else if (pt.style === 'circle') {
                point.setAttributeNS(null, 'cx', pt.x);
                point.setAttributeNS(null, 'cy', pt.y);
                point.setAttributeNS(null, 'r', pt.radius);
            }

            self.element.appendChild(point);
        });
    }
}

Graph.prototype.render_seasonal_trendline = function() {
    var point = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    var points_string = '';
    
    for (x in this.means.x) {
        var y = this.means.x[x]
        
        points_string += x + ',' + y + ' ';
    }
    
    point.classList.add('chart-trendline');
    point.setAttributeNS(null, 'points', points_string);
    this.element.appendChild(point);
}
