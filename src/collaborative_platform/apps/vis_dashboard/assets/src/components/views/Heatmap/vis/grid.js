import * as d3 from 'd3';

function regularGrid(canvas, overlayCanvas, padding, axisWidth, legendWidth, data, colorScale, rangeScale){
	const [concurrenceMatrix, maxRelated] = data;

	const minSpacingX = 2*padding + axisWidth + legendWidth,
		minSpacingY = 2*padding + (axisWidth * Math.cos(Math.PI / 4)),
		sideLength = Math.min(canvas.width - minSpacingX, canvas.height - minSpacingY),
		leftOffset = canvas.width - (sideLength + legendWidth + padding),
		maxLabels = Math.max(Object.keys(concurrenceMatrix).length, Object.values(concurrenceMatrix)[0].length);

	const gridScale = d3.scaleBand()
		.domain(d3.range(maxLabels))
		.range([0, sideLength])
		.round(true)
		.padding(.1);

	const context = canvas.getContext("2d");
	context.save();

	Object.entries(concurrenceMatrix).forEach(([entity, intersections], i)=>{
		intersections.forEach((intersection, j)=>{
			context.fillStyle = colorScale(rangeScale(intersection.length));
			context.fillRect(leftOffset + gridScale(i), padding + gridScale(j), gridScale.bandwidth(), gridScale.bandwidth());
		});
	});

	context.restore();
}

function stairGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

function tiltedGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

export default {regularGrid, stairGrid, tiltedGrid}