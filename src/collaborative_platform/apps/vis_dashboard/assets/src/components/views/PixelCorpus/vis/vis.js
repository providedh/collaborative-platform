import * as d3 from 'd3';

import docSorting from './docSorting';
import renderLegend from './legend';
import renderEntities from './entities';
//import renderCertainty from './certainty';

/* Class: Vis
 *
 * 
 * */
export default function Vis(){
	const self = {
		_taxonomy: null,
		_docSortingCriteria: null,
		_entitySorting: null,
		_colorCertaintyBy: null,
		_entityColorScale: null,
		_certaintyColorScale: null,
		_eventCallback: null,
		_padding: 10,
		_innerMargin: 50,
		_legendWidth: 120,
		_titleHeight: 60,
		_maxRowItems: 15,
		_docNameWidth: 165,
	};

	function _init(){
		self.setTaxonomy = _setTaxonomy;
		self.setDocSortingCriteria = _setDocSortingCriteria;
		self.setEntitySortingCriteria = _getParameterSetter('_entitySortingCriteria');
		self.setColorCertaintyBy = _setColorCertaintyBy;
		self.setEventCallback = _getParameterSetter('_eventCallback');
		self.render = _render;

		return self;
	}

	function _getParameterSetter(key){
		return (value)=>self[key]=value;
	}

	function _setDocSortingCriteria(name){
		if(docSorting.hasOwnProperty(name))
			self._docSorting = docSorting[name]
		else
			self._docSorting = Object.values(docSorting)[0]
	}	

	function _setTaxonomy(taxonomy){
		self._taxonomy = taxonomy;
		self._entityColorScale = d3.scaleOrdinal()
			.domain(Object.keys(taxonomy.entities))
			.range(Object.values(taxonomy.entities).map(e=>e.color));
	}

	function _setColorCertaintyBy(colorCertaintyBy){
		self._colorCertaintyBy = colorCertaintyBy;
		self._certaintyColorScale = d3.interpolateOrRd;
	}

	function _render(container, svg, entityData, certaintyData){
		if(svg == null  || entityData == null || certaintyData == null)
			return;

		svg.setAttribute('width', container.clientWidth);
		svg.setAttribute('height', container.clientHeight);

		const docOrder = self._docSorting(entityData.all, null),
			freeSpace = container.clientWidth - (self._padding*2 + self._innerMargin + self._legendWidth + self._docNameWidth*2),
			columnWidth = freeSpace/2;

		if(entityData.all.length > 0){
			renderEntities(Object.assign({}, self, {svg, docOrder, columnWidth, data: entityData}));
		}

		//if(entityData.all.length > 0){
		//	renderCertainty(Object.assign({}, self, {svg, docOrder, columnWidth, data: entityData}));
		//}

		renderLegend(svg, self._legendWidth, self._padding, self._entityColorScale, self._certaintyColorScale, self._colorCertaintyBy);
	}

	return _init();
}