function init() {
    // Set SVG width and height
    var w = 300;
    var h = 300;
    
    // Data for the pie chart
    var dataset = [5, 6, 10, 20, 25, 45];

    // Set the outer and inner radius for the pie chart
    var outerRadius = w/2;
    var innerRadius = 0;

    // Create an arc generator with the specified radii
    var arc = d3.arc()
                  .outerRadius(outerRadius)
                  .innerRadius(innerRadius);

    // Create a pie layout generator
    var pie = d3.pie();

    // Create the SVG container
    var svg = d3.select("#chart")
                  .append("svg")
                  .attr("width", w)
                  .attr("height", h);

    // Create a group for each arc and position them in the center
    var arcs = svg.selectAll("g.arc")
                    .data(pie(dataset))
                    .enter()
                    .append("g")
                    .attr("class", "arc")
                    .attr("transform", "translate(" + outerRadius + "," + outerRadius + ")");
                    
    // Create a color scale for the pie slices
    var color = d3.scaleOrdinal(d3.schemeCategory10);

    // Draw each pie slice with a different color
    arcs.append("path")
        .attr("fill", function(d, i) {
          return color(i)
        })
        .attr("d", function(d, i) {
          return arc(d, i)
        });

    // Add text labels to each slice, positioned at the centroid
    arcs.append("text")
        .text(function(d){
          return d.value
        })
        .attr("transform", function(d){
          return "translate(" + arc.centroid(d) +")";
        })
        .attr("font-size", "20px")
  }
  
  window.onload = init;
