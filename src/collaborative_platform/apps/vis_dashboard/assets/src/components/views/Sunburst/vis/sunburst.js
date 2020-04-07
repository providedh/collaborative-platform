import * as d3 from 'd3';

/* Class: Heatmap
 *
 * 
 * */
export default function Sunburst(){
	const self = {
		_eventCallback: null,
		_padding: 10,
		_legendWidth: 120,
		_hoverTooltipHeight: 70,
		_getLegendHeight: numLevels=>numLevels*70,
	};

	function _init(){
		self.setEventCallback = _getParameterSetter('_eventCallback');
		self.render = _render;

		return self;
	}

	function _getParameterSetter(key){
		return (value)=>self[key]=value;
	}

	function setupColorSchemes(){
		self._colorSchemes = {
			author: d3.scaleOrdinal().range(d3.schemePaired),
			document: d3.scaleOrdinal().range(d3.schemePaired),
			category: d3.scaleOrdinal()
				.range(Object.values(settings.taxonomy).map(x=>x.color))
				.domain(Object.values(settings.taxonomy).map(x=>x.name)),
			attribute: d3.scaleOrdinal().range(d3.schemePaired),
			degree: d3.interpolateYlOrRd,
			certainty: d3.scaleOrdinal()
				.range(d3.schemeYlOrRd(5))
				.domain(['unknown', 'very low', 'low', 'medium', 'high', 'very high'])
		}
	}

	function renderLegend(width, height, levels, containerRef){

	}

	function setupHoverTooltip(){

	}

	function renderSunburst(width, height, data, numLevels, levels, containerRef){

	}

	function _render(width, height, data, numLevels, levels, containerRef){
		console.log(width, height, data, numLevels, levels, containerRef)
	}

	return _init();
};