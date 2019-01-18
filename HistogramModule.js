// var HistogramModule = function() {
//   var x = [];
// for (var i = 0; i < 500; i ++) {
// 	x[i] = Math.random();
// }
//
// var trace = {
//     x: x,
//     type: 'histogram',
//   };
// var data = [trace];
// Plotly.newPlot('myDiv', data);
// }

var HistogramModule = function(bins) {
    // Create the elements

    console.log("I am making the Histogram right now!");
    // $("body").append(canvas)
    // Create the tag:
    var canvas_tag = "<canvas width='" + 100 + "' height='" + 100 + "' ";
    canvas_tag += "style='border:1px dotted'></canvas>";
    // Append it to body:
    var canvas = $(canvas_tag)[0];
    $("elements").append(canvas);
    // // Create the context and the drawing controller:
    // var context = canvas.getContext("2d");

    console.log("Still working! ;-)");

    // Prep the chart properties and series:
    // var datasets = [{
    //     label: "Data",
    //     fillColor: "rgba(151,187,205,0.5)",
    //     strokeColor: "rgba(151,187,205,0.8)",
    //     highlightFill: "rgba(151,187,205,0.75)",
    //     highlightStroke: "rgba(151,187,205,1)",
    //     data: []
    // }];
    //
    // // Add a zero value for each bin
    // for (var i in bins)
    //     datasets[0].data.push(0);
    //
    // var data = {
    //     labels: bins,
    //     datasets: datasets
    // };

    // var options = {
    //     scaleBeginsAtZero: true
    // };

    console.log("I have just made all the settings, now onto the graph");

    // Create the chart object
    var chart = new Chart(context).Bar(data, options);

    this.render = function(data) {
        for (var i in data)
            chart.datasets[0].data[i] = data[i];
        chart.update();
    };

    this.reset = function() {
        chart.destroy();
        chart = new Chart(context).Bar(data, options);
    };
};
