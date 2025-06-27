function init() {
    var w = 300; // SVG width
    var h = 300; // SVG height
    
    // Sample dataset: each object represents a group with apples, oranges, grapes
    var dataset = [
      {apples: 5, oranges: 10, grapes: 22},
      {apples: 4, oranges: 12, grapes: 28},
      {apples: 2, oranges: 19, grapes: 32},
      {apples: 7, oranges: 23, grapes: 35},
      {apples: 23, oranges: 17, grapes: 43}
    ];

    // Create a stack generator for the specified keys
    var stack = d3.stack()
                  .keys(["apples", "oranges", "grapes"]);

    // Apply the stack generator to the dataset
    var series = stack(dataset);

    // Create the SVG container
    var svg = d3.select("#chart")
                  .append("svg")
                  .attr("width", w)
                  .attr("height", h);

    // Create a band scale for the x-axis (one band per group)
    var xScale = d3.scaleBand()
                    .domain(dataset.map(function(d, i) {
                      return i;
                    }))
                    .range([0, w])
                    .padding(0.1);

    // Create a linear scale for the y-axis (stacked total)
    var yScale = d3.scaleLinear()
                    .domain([0, d3.max(dataset, function(d){
                      return d.apples + d.oranges + d.grapes;
                    })])
                    .range([h, 0]);

    // Ordinal color scale for each stack series
    var color = d3.scaleOrdinal(d3.schemeCategory10);

    // Create a group for each series (apples, oranges, grapes)
    var group = svg.selectAll("g")
                    .data(series)
                    .enter()
                    .append("g")
                    .style("fill", function(d, i){
                      return color(i); // Assign color to each group
                    });

    // Draw a rectangle for each segment in the stack
    var rects = group.selectAll("rect")
                      .data(function(d){ return d; }) // d is an array of [y0, y1] for each group
                      .enter()
                      .append("rect")
                      .attr("x", function(d, i) {
                        return xScale(i); // Position by group index
                      })
                      .attr("y", function(d, i){
                        return yScale(d[1]); // Top of the segment
                      })
                      .attr("height", function(d) {
                        return yScale(d[0]) - yScale(d[1]); // Height of the segment
                      })
                      .attr("width", xScale.bandwidth()); // Width of each bar
}
  
window.onload = init;
