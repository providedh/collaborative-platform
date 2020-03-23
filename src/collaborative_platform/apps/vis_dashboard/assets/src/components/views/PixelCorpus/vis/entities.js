import * as d3 from 'd3';

export default function renderEntities(args){
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

	const entitiesByDoc = getEntitiesPerDoc(data),
		rowsByDoc = getRowsByDoc(entitiesByDoc, _maxRowItems);

	const {width, height} = svg.getBoundingClientRect(),
		rootG = d3.select(svg)
			.select('g.entities')
			.attr('transform', `translate(${_padding}, ${_padding})`),
		cellPadding = 3,
		cellSide = getCellSide(rowsByDoc, columnWidth, height-(_padding*2 + _titleHeight), cellPadding, _maxRowItems);

	// render title
	rootG.select('.title')
		.attr('x', 0)
		.attr('y', 22)// font size
		.text('Entities in the corpus');

	renderDocumentLabels(docOrder, rowsByDoc, rootG, cellSide, cellPadding, _titleHeight);

	renderEntityCells(docOrder, entitiesByDoc, rowsByDoc, rootG, cellSide, cellPadding, _titleHeight, _docNameWidth, _maxRowItems, _entityColorScale);

	setupInteractions();
}

function priorRows(doc, rowsByDoc, docOrder){
	const docIndex = docOrder[doc],
		rowCount = Object.entries(docOrder)
			.reduce((ac,[name, idx])=>ac+(idx<docIndex?rowsByDoc[name]:0),0);
	return rowCount
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

function renderDocumentLabels(docOrder, rowsByDoc, rootG, cellSide, cellPadding, titleHeight){
	let labels = rootG.select('.docLabels')
		.attr('transform', `translate(0, ${titleHeight})`)
		.selectAll('text.label')
		.data(Object.keys(docOrder));
	labels.exit().remove();
	labels.enter().append('svg:text').classed('label', true);

	rootG.select('.docLabels').selectAll('text.label')
		.text(d=>shorttenedLabel(d))
		.attr('x', 0)
		.transition()
			.duration(750)
	    	.ease(d3.easeLinear)
			.attr('y', d=>priorRows(d, rowsByDoc, docOrder)*(cellSide + cellPadding));
}

function renderEntityCells(docOrder, data, rowsByDoc, rootG, cellSide, cellPadding, titleHeight, docNameWidth, maxRowItems, colorScale){
	let labels = rootG.select('.entityCells')
		.attr('transform', `translate(${docNameWidth}, ${titleHeight - 22})`)
		.selectAll('g.doc')
		.data(Object.keys(docOrder));
	labels.exit().remove();
	labels.enter().append('svg:g').classed('doc', true);
	rootG.select('.entityCells').selectAll('g.doc')
		.each(function(d){
			const rects = d3.select(this)
				.selectAll('rect')
				.data(data[d].map((x,i)=>Object.assign(x,{i})));
			rects.exit().remove();
			rects.enter().append('svg:rect')
		})
		.transition()
			.duration(750)
	    	.ease(d3.easeLinear)
			.attr('transform', d=>`translate(0, ${priorRows(d, rowsByDoc, docOrder)*(cellSide+cellPadding)})`);

	rootG.select('.entityCells').selectAll('rect')
		.attr('width', cellSide)
		.attr('height', cellSide)
		.attr('x', d=>(cellSide + cellPadding)*(d.i%maxRowItems))
		.attr('y', d=>(cellSide + cellPadding)*Math.trunc(d.i/maxRowItems))
		.attr('stroke', 'black')
		.attr('fill', d=>colorScale(d.type))
}

function setupInteractions(){

}

function getEntitiesPerDoc(data){
	const entitiesByDoc = {};
	data.all.forEach(e=>{
		if(!entitiesByDoc.hasOwnProperty(e.file_name))
			entitiesByDoc[e.file_name] = [];
		entitiesByDoc[e.file_name].push(e);
	});
	return entitiesByDoc;
}

function getRowsByDoc(entitiesByDoc, maxRowItems){
	const rowsByDoc = Object.fromEntries( // for entries [doc, lineCount]
		Object.entries(entitiesByDoc)
		.map(([doc, entities])=>[doc, 1+
			(entities.length<=maxRowItems?0:Math.trunc(entities.length/maxRowItems))]));

	return rowsByDoc;
}

function getCellSide(rowsByDoc, columnWidth, columnHeight, cellPadding, maxRowItems){
	const rows = Object.values(rowsByDoc).reduce((ac,dc)=>ac+dc, 0),
		sideFittedByHeight = (columnHeight-(rows-1)*cellPadding) / rows,
		sideFittedByWidth = (columnWidth-(maxRowItems-1)*cellPadding) / maxRowItems,
		sideLength = Math.min(sideFittedByHeight, sideFittedByWidth);
	return sideLength;
}