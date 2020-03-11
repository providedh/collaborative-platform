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
		_padding: 10,
		_axisWidth: 30
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

	function _render(data, container, canvas, overlayCanvas){
		if(container == null || canvas == null || overlayCanvas == null || data == null || data.length == 0)
			return;

		canvas.width = container.clientWidth;
		canvas.height = container.clientHeight;
	    overlayCanvas.width = container.clientWidth;
	    overlayCanvas.height = container.clientHeight;
		
	    const context = canvas.getContext("2d");
	    context.clearRect(0, 0, canvas.width, canvas.height);

	    self._gridRenderer(
    		canvas, 
    		overlayCanvas, 
    		self._padding, 
    		self._axisWidth, 
    		data, 
    		self._colorScale, 
    		self._rangeScale);

		//console.log('rendering', {
		//	data,
		//	colorScale: self._colorScale,
		//	rangeScale: self._rangeScale,
		//	gridRenderer: self._gridRenderer,
		//	axisRenderer: self._axisRenderer,
		//	});
	}

	return _init();
}