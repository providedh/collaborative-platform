import * as d3 from 'd3';
import setupBrush from './brush';
/* Class: Heatmap
 *
 * 
 * */
export default function Heatmap(){
	const self = {
		_taxonomy: null,
		_docSortingCriteria: null,
		_entitySortingCriteria: null,
		_certaintyProperty: null,
		_eventCallback: null,
		_padding: 10,
		_innerMargin: 30,
		_legendWidth: 120,
		_titleHeight: 60,
		_maxRowItems: 30,
		_docNameWidth: 50,
	};

	function _init(){
		self.setTaxonomy = _getParameterSetter('_taxonomy');
		self.setDocSortingCriteria = _getParameterSetter('_docSortingCriteria');
		self.setEntitySortingCriteria = _getParameterSetter('_entitySortingCriteria');
		self.setCertaintyProperty = _getParameterSetter('_certaintyProperty');
		self.setEventCallback = _getParameterSetter('_eventCallback');
		self.render = _render;

		return self;
	}

	function _getParameterSetter(key){
		return (value)=>self[key]=value;
	}

	function _render(svg, entityData, certaintyData){
		if(svg == null  || data == null || data.length == 0)
			return;

		const [docOrder, maxItemCount] = sortDocuments(entityData, self._docSortingCriteria),
			freeSpace = svg.width - (self._padding*2 + self._innerMargin + self._legendWidth),
			columnWidth = freeSpace/2,
			args = {svg, width, maxItemCount, docOrder, margin:_innerMargin, taxonomy:self._taxonomy, entitySorting: self._entitySortingCriteria};

		renderEntities(Object.assign({}, args, {data: entityData}));
		renderCertainty(Object.assign({}, args, {data: certaintyData}));
		renderLegend(svg, _legendWidth, padding)
	}

	return _init();
}