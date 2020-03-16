import * as d3 from 'd3';
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
		_axisWidth: 30,
		_legendWidth: 80
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

	function _renderColorLegend(canvas){
		const width = 60, 
			height = 200,
			topPadding = 10,
			titleHeight = 25,
			colorWidth = 30,
			colorHeight = height-titleHeight,
			x = canvas.width - self._padding - self._legendWidth,
			y = self._padding + self._axisWidth + titleHeight + topPadding,
			legendscale = i=>i/colorHeight,
			ticks = 7;

		const ctx = canvas.getContext("2d");
		ctx.save();

		// image data hackery based on http://bl.ocks.org/mbostock/048d21cf747371b11884f75ad896e5a5
		d3.range(colorHeight).forEach(function(i) {
		    ctx.strokeStyle = self._colorScale(legendscale(i));
		    ctx.beginPath();
		    ctx.moveTo(x, y+i);
		    ctx.lineTo(x+colorWidth, y+i);
		    ctx.stroke();
		  });

		ctx.moveTo(0,0);
		ctx.strokeStyle = 'black';
		ctx.strokeRect(x, y, colorWidth, colorHeight);

		ctx.font = '13px Open Sans';
		ctx.fillText('Occurrences', x, y - titleHeight + 5);

		ctx.font = '10px Open Sans';
		d3.range(ticks+1).forEach(function(i){
			const rectIdx = (colorHeight/ticks)*i,
				tickY = y + rectIdx,
				value = Math.floor(self._rangeScale.invert(i/ticks));

			ctx.beginPath();
		    ctx.moveTo(x+colorWidth, tickY);
		    ctx.lineTo(x+colorWidth+10, tickY);
		    ctx.stroke();
			ctx.fillText(value, x+colorWidth+15, tickY);
		});

		ctx.restore();
	}

	function _render(data, container, canvas, overlayCanvas){
		if(container == null || canvas == null || overlayCanvas == null || data == null || data.length == 0)
			return;

		const [_, maxRelated] = data;
		self._rangeScale.domain([0, maxRelated]);

		canvas.width = container.clientWidth;
		canvas.height = container.clientHeight;
	    overlayCanvas.width = container.clientWidth;
	    overlayCanvas.height = container.clientHeight;
		
	    const context = canvas.getContext("2d");
	    context.clearRect(0, 0, canvas.width, canvas.height);

	    _renderColorLegend(canvas);

	    self._gridRenderer(
    		canvas, 
    		overlayCanvas, 
    		self._padding, 
    		self._axisWidth, 
    		self._legendWidth,
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