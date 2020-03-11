import * as d3 from 'd3';

function regularGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	const names = Object.keys(data);

	const width = Math.min(canvas.width, canvas.height) - 2*padding - axisWidth;

	const gridScale = d3.scaleBand()
		.domain(names)
		.range([padding + axisWidth, width])
		.round(true)
		.padding(.1);

	const context = canvas.getContext("2d");
	context.save();

	Object.entries(data).forEach(([entity, intersections])=>{
		//console.log(entity, intersections)
		intersections.forEach((intersection, i)=>{
			//context.moveTo(gridScale(entity), gridScale(names[i]));

			//console.log(intersection.length, rangeScale(intersection.length), colorScale(intersection.length), colorScale(rangeScale(intersection.length)))
			context.fillStyle = colorScale(intersection.length);
			//console.log(gridScale(entity), gridScale(names[i]), gridScale.bandwidth(), gridScale.bandwidth())
			context.fillRect(gridScale(entity), gridScale(names[i]), gridScale.bandwidth(), gridScale.bandwidth());
		});
	});

	context.restore();
}

function stairGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

function tiltedGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

export default {regularGrid, stairGrid, tiltedGrid}