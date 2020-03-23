import * as d3 from 'd3';

export default function renderEntities(args){
	console.log(args)
	const {
		svg,
		docOrder, 
		data,
		columnWidth,
		_entitySortingCriteria,
		_entityColorScale,
		_eventCallback,
		_padding,
		_titleHeight,
		_maxRowItems,
		_docNameWidth 
		} = args;

	const entitiesByDoc = {};
	data.all.forEach(e=>{
		if(!entitiesByDoc.hasOwnProperty(e.file_id))
			entitiesByDoc[e.file_id] = [];
		entitiesByDoc[e.file_id].push(e);
	})

	const {width, height} = svg.getBoundingClientRect(),
		rootG = d3.select(svg)
			.select('g.entities')
			.attr('transform', `translate(${_padding}, ${_padding})`),
		cellPadding = 2,
		cellSide = getCellSide(entitiesByDoc, columnWidth, height-(_padding*2), cellPadding, _maxRowItems);

	// render title
	rootG.select('.title')
		.attr('x', 0)
		.attr('y', 22)// font size
		.text('Entities in the corpus');

	renderDocumentLabels(docOrder, rootG, cellSide, cellPadding, _titleHeight);

	renderEntityCells();

	setupInteractions();
}

function shorttenedLabel(label, maxLabelLength = 20){
	if(label.length <= maxLabelLength)
		return label;

	const overflow = label.length - maxLabelLength,
		fragmentLength = Math.trunc(maxLabelLength/2 - 2),
		startFragment = label.slice(0, fragmentLength),
		endFragment = label.slice(label.length - fragmentLength, label.length);
	return startFragment + '...' + endFragment;
}

function renderDocumentLabels(docOrder, rootG, cellSide, cellPadding, titleHeight){
	let labels = rootG.select('.docLabels')
		.attr('transform', `translate(0, ${titleHeight})`)
		.selectAll('text.label')
		.data(docOrder);
	labels.exit().remove();
	labels.enter().append('svg:text').classed('label', true);

	rootG.select('.docLabels').selectAll('text.label')
		.text(x=>shorttenedLabel(x))
		.transition()
			.attr('x', 0)
			.attr('y', (x, i)=>i*(cellSide + cellPadding));
}

function renderEntityCells(){

}

function setupInteractions(){

}

function getCellSide(entitiesByDoc, columnWidth, columnHeight, cellPadding, maxRowItems){
	const rows = Object.values(entitiesByDoc).reduce((ac,dc)=>ac+1+Math.trunc(dc.length/maxRowItems),0),
		sideFittedByHeight = (columnHeight-(rows-1)*cellPadding) / rows,
		sideFittedByWidth = (columnWidth-(maxRowItems-1)*cellPadding) / maxRowItems,
		sideLength = Math.min(sideFittedByHeight, sideFittedByWidth);
		
	return sideLength;
}