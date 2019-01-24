var ContinuousVisualization = function(height, width, context) {
	// idk why we have to calculate the ratio here, but this seems to work
	var ratio = height / width
	// just found out I have to calculate ratio2 here as well...??? this makes so little sense
	var ratio2 = width / height
	var height = height * ratio2;
	var width = width * ratio;
	var context = context;

	this.draw = function(objects) {
		for (var i in objects) {
			var p = objects[i];

			if (p.Shape == "rect"){
				this.drawRectangle(p.x, p.y, p.w, p.h, p.Color);
			}
			else if (p.Shape == 'circle'){
				this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled);
			};
		};
	};

	this.drawCircle = function(x, y, radius, color, fill) {
		console.log(radius)
		var cx = x * width;
		var cy = y * height;
		var r = radius;
		context.beginPath();
		context.arc(cx, cy, r, 0, Math.PI * 2, false);
		context.closePath();

		context.strokeStyle = color;
		context.stroke();

		if (fill) {
			context.fillStyle = color;
			context.fill();
		}

	};

	this.drawRectangle = function(x, y, w, h, color) {
		var cx = x * width - 1/2 * w;
		var cy = y * height - 1/2 * h;
		context.fillStyle = color;
		context.fillRect(cx, cy, w, h);
		context.stroke();
	};

	this.resetCanvas = function() {
		context.clearRect(0, 0, 9999, 9999);
		context.beginPath();
	};
};

var SimpleContinuousModule = function(canvas_width, canvas_height) {
	// Create the tag:
	var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
	canvas_tag += "style='border:1px dotted'></canvas>";
	// Append it to body:
	var canvas = $(canvas_tag)[0];
	$("body").append(canvas);

	// Create the context and the drawing controller:
	var context = canvas.getContext("2d");
	var canvasDraw = new ContinuousVisualization(canvas_width, canvas_height, context);

	this.render = function(data) {
		canvasDraw.resetCanvas();

		//  draw the road (This color is Asphalt grey :-P)
		context.fillStyle = "#282B2A";
		context.fillRect(0, 307, canvas_width, 135)
		context.stroke()

		// draw the middle part of the road
		context.fillStyle = "#2CB037";
		context.fillRect(0, 368, canvas_width, 14)
		context.stroke()

		// draw zebra crossings
		ys_zebra = [314, 333, 352, 388, 406, 425]
		for (var i in ys_zebra) {
			var p = ys_zebra[i];
			var zebra_width = 60
			context.fillStyle = "White";
			context.fillRect((canvas_width/2) - (zebra_width/2),p,zebra_width,7)
			context.stroke()
		};

		// draw agents
		canvasDraw.draw(data);

	};

	this.reset = function() {
		canvasDraw.resetCanvas();
	};

};
