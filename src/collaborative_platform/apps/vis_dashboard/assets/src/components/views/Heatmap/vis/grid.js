import * as d3 from 'd3';

function regularGrid(canvas, overlayCanvas, padding, axisWidth, legendWidth, data, colorScale, rangeScale){
	const [concurrenceMatrix, maxRelated] = data,
		names = Object.keys(concurrenceMatrix);

	const width = Math.min(canvas.width - legendWidth, canvas.height) - 2*padding - axisWidth,
		leftOffset = canvas.width - (width + 2*padding + axisWidth + legendWidth);

	const gridScaleX = d3.scaleBand()
		.domain(names)
		.range([padding + axisWidth + leftOffset, width + leftOffset])
		.round(true)
		.padding(.1);
	const gridScaleY = d3.scaleBand()
		.domain(names)
		.range([padding + axisWidth, width])
		.round(true)
		.padding(.1);

	const context = canvas.getContext("2d");
	context.save();

	Object.entries(concurrenceMatrix).forEach(([entity, intersections])=>{
		//console.log(entity, intersections)
		intersections.forEach((intersection, i)=>{
			//context.moveTo(gridScale(entity), gridScale(names[i]));
			//console.log(intersection.length, rangeScale(intersection.length), colorScale(intersection.length), )
			context.fillStyle = colorScale(rangeScale(intersection.length));
			//console.log(gridScale(entity), gridScale(names[i]), gridScale.bandwidth(), gridScale.bandwidth())
			context.fillRect(gridScaleX(entity), gridScaleY(names[i]), gridScaleX.bandwidth(), gridScaleX.bandwidth());
		});
	});

	context.restore();
}

function stairGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

function tiltedGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

export default {regularGrid, stairGrid, tiltedGrid}