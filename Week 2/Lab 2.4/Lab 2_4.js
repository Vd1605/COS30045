function init(){
    var w = 700;
    var h = 150;
    var barPadding = 2;

    d3.csv("Task_2_4_data.csv").then(function(data) {
        console.log(data);
        wombatSightings = data;
        barChart(wombatSightings);
    });

    var svg = d3.select("#chart")
                .append("svg")
                .attr("width", w)
                .attr("height", h);
    
    function barChart() {
        svg.selectAll("rect")
        .data(wombatSightings)
        .enter()
        .append("rect")
        .attr("x", function(d, i){
            return i * (w/wombatSightings.length);
        })
        .attr("y", function(d){
            return h - (d.wombats*4);
        })
        .attr("width", (w/wombatSightings.length)-barPadding)
        .attr("height", function(d){
            return d.wombats*4;
        })
        .attr("fill", function(d){
            return d.wombats > 10 ? "darkblue" : "lightblue";
        })
        .on("mouseover", function(event, d, i) {
            // Highlight bar
            d3.select(this).attr("fill", "grey");
            // Add text on the bar
            svg.append("text")
                .attr("class", "bar-label")
                .attr("x", +d3.select(this).attr("x") + (+d3.select(this).attr("width")/2))
                .attr("y", +d3.select(this).attr("y") - 5)
                .attr("text-anchor", "middle")
                .attr("font-size", "12px")
                .attr("fill", "black")
                .text(d.wombats);
        })
        .on("mousemove", function(event) {
            d3.select("#tooltip")
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 20) + "px");
        })
        .on("mouseout", function(event, d) {
            d3.select(this).attr("fill", d.wombats > 10 ? "darkblue" : "lightblue");
            svg.selectAll(".bar-label").remove();
        });
    }

    
}
window.onload = init;