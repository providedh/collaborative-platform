import * as d3 from 'd3';

function shorttenedLabel(label, maxLabelLength = 30){
	if(label.length <= maxLabelLength)
		return label;

	const overflow = label.length - maxLabelLength,
		fragmentLength = Math.trunc(maxLabelLength/2 - 2),
		startFragment = label.slice(0, fragmentLength),
		endFragment = label.slice(label.length - fragmentLength, label.length);
	return startFragment + '...' + endFragment;
} 

function regularAxis(canvas, padding, axisWidth, legendWidth, data){
	const {concurrenceMatrix, axis1, axis2} = data;

	const minSpacingX = 2*padding + axisWidth + legendWidth,
		minSpacingY = 2*padding + (axisWidth * Math.cos(Math.PI / 4)),
		sideLength = Math.min(canvas.width - minSpacingX, canvas.height - minSpacingY),
		leftOffset = canvas.width - (sideLength + legendWidth + padding),
		bottomOffset = canvas.height - (sideLength + padding),
		maxLabels = Math.max(axis1.values.length, axis2.values.length),
		leftLabelLength = (leftOffset - 2*padding) / 7,
		bottomLabelLength = ((bottomOffset - 2*padding) / Math.cos(Math.PI / 4)) / 7;

	const gridScale = d3.scaleBand()
		.domain(d3.range(maxLabels))
		.range([0, sideLength])
		.round(true)
		.padding(.1);

	const ctx = canvas.getContext("2d");
	ctx.save();

	ctx.textAlign = 'end';
	ctx.textBaseline = 'middle';
	ctx.font = '13px Open Sans';
	axis1.values.forEach((label, i)=>{
		ctx.fillText(shorttenedLabel(label, leftLabelLength), leftOffset, padding + gridScale(i) + gridScale.bandwidth()/2);
	});
	ctx.restore()

	ctx.save()
	ctx.textAlign = 'end';
	ctx.textBaseline = 'middle';
	ctx.font = '13px Open Sans';

	axis2.values.forEach((label, i)=>{
		const bandMiddle = gridScale(i) + gridScale.bandwidth()/2,
			x = leftOffset +  bandMiddle,
			y = padding*2 + gridScale(axis1.values.length),
			translatedX = x,
			translatedY = y;

			ctx.save()
			ctx.translate(translatedX, translatedY);
			ctx.rotate(-Math.PI / 4);
			ctx.translate(-translatedX, -translatedY);

			ctx.fillText(shorttenedLabel(label, bottomLabelLength), translatedX, translatedY);
			ctx.restore()
	});

	ctx.restore();
}

function tiltedAxis(canvas, overlayCanvas, padding, axisWidth, data, colorScale, rangeScale){
	
}

export default {regularAxis, tiltedAxis}