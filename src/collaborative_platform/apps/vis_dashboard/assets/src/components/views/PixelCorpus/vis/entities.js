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

	const entitiesByDoc = {};
	data.all.forEach(e=>{
		if(!entitiesByDoc.hasOwnProperty(e.file_id))
			entitiesByDoc[e.file_id] = [];
		entitiesByDoc[e.file_id].push(e);
	})

	const {width, height} = svg.getBoundingClientRect(),
		rootG = d3.select(svg).select('g.entities'),
		cellPadding = 2,
		cellSide = getCellSide(entitiesByDoc, columnWidth, height-(_padding*2), cellPadding, _maxRowItems);

}

function getCellSide(entitiesByDoc, columnWidth, columnHeight, cellPadding, maxRowItems){
	const rows = Object.values(entitiesByDoc).reduce((ac,dc)=>ac+1+Math.trunc(dc.length/maxRowItems),0),
		sideFittedByHeight = (columnHeight-(rows-1)*cellPadding) / rows,
		sideFittedByWidth = (columnWidth-(maxRowItems-1)*cellPadding) / maxRowItems,
		sideLength = Math.min(sideFittedByHeight, sideFittedByWidth);
		
	return sideLength;
}