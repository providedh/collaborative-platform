/* Class: Heatmap
 *
 * 
 * */
export default function Heatmap(){
	const self = {
		_colorScale: null,
		_rangeScale: null,
		_gridRenderer: null,
		_axisRenderer: null,
		_eventCallback: null,
	};

	function _init(){

		self.setRangeScale = _getParameterSetter('_rangeScale');
		self.setColorScale = _getParameterSetter('_colorScale');
		self.setGridRenderer = _getParameterSetter('_gridRenderer');
		self.setAxisRenderer = _getParameterSetter('_axisRenderer');
		self.setEventCallback = _getParameterSetter('_eventCallback');
		self.render = _render;

		return self;
	}

	function _getParameterSetter(key){
		return (value)=>self[key]=value;
	}

	function _render(data, refContainer, refCanvas, refOverlayCanvas){
		console.log('rendering', {
			colorScale: self._colorScale,
			rangeScale: self._rangeScale,
			gridRenderer: self._gridRenderer,
			axisRenderer: self._axisRenderer,
			});
	}

	return _init();
}