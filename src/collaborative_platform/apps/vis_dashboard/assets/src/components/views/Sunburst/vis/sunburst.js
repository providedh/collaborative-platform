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

	function _render(width, height, data, numLevels, levels, containerRef){
		console.log(width, height, data, numLevels, levels, containerRef)
	}

	return _init();
};