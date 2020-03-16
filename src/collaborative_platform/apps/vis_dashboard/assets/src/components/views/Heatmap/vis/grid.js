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

	setupInteractions(concurrenceMatrix, canvas, overlayCanvas, leftOffset, padding, gridScale);
}

function setupInteractions(matrix, canvas, overlayCanvas, leftOffset, padding, gridScale){
    const context = overlayCanvas.getContext("2d");

    function handleOverlayHover(e){
        const [x, y] = d3.mouse(this),
        	xAxisIndex = Math.floor((y - padding) / gridScale.step()),
        	yAxisIndex = Math.floor((x - leftOffset) / gridScale.step());

        let shared = null;
        if(yAxisIndex >= 0 && yAxisIndex < Object.keys(matrix).length){
			if(xAxisIndex >= 0 && xAxisIndex < Object.values(matrix)[yAxisIndex].length){
        		shared = Object.values(matrix)[yAxisIndex][xAxisIndex];
        	}        	
        }

        if(shared == null)
        	return;

        context.clearRect(0,0,overlayCanvas.width, overlayCanvas.height);
        
        context.save()
        context.fillStyle = '#f8f9fa';
        context.strokeStyle = '#00b3b0';
        context.beginPath();
        context.rect(x+5, y-10, Math.max(...shared.map(x=>x.length))*6+5,shared.length*20)
        context.stroke();
        context.fill();
        context.closePath();
        context.textBaseline = 'bottom';
        context.fillStyle = '#00b3b0';
        shared.forEach((t,i)=>
        	context.fillText(t,x+10, y+5+(i*20)));
        context.restore()
    }

    d3.select(canvas)
        .on('mousemove', handleOverlayHover);
}

function stairGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

function tiltedGrid(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

export default {regularGrid, stairGrid, tiltedGrid}