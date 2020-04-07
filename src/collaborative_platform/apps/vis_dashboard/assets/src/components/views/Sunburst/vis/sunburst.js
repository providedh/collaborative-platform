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
		_getLegendHeight: numLevels=>numLevels*0,
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
				.range(d3.schemeYlOrRd[5])
				.domain(['unknown', 'very low', 'low', 'medium', 'high', 'very high'])
		}
	}

	function renderLegend(width, height, levels, container){

	}

	function renderInnerCircle(annotationsCount, centerX, centerY, innerCircleRadius, container){
		d3.select(container).select('svg').selectAll('g.innerCircle')
			.data([annotationsCount])
			.enter().append('svg:g')
			.attr('class', 'innerCircle')
			.each(function(d){
				d3.select(this)
					.append('svg:circle')
					.attr('r', innerCircleRadius)
					.attr('cx', innerCircleRadius)
					.attr('cy', innerCircleRadius);
				d3.select(this)
					.append('svg:text')
					.attr('class', 'annotations')
					.attr('x', innerCircleRadius)
					.attr('y', innerCircleRadius - 4)
				d3.select(this)
					.append('svg:text')
					.attr('x', innerCircleRadius)
					.attr('y', innerCircleRadius + 12)
					.text('annotations')
			})

		d3.select(container).select('svg').selectAll('g.innerCircle')
			.attr('transform', `translate(${centerX - innerCircleRadius}, ${centerY - innerCircleRadius})`)
			.each(function(d){
				d3.select(this).select('text.annotations').text(d);
			})
	}

	function setupHoverTooltip(){

	}

	function renderSunburst(data, numLevels, levels, container){
		const height = container.clientHeight,
			width = container.clientWidth,
			freeVspace = height - (self._padding*2 + self._hoverTooltipHeight + self._getLegendHeight(numLevels)),
			freeHspace = width - (self._padding * 2),
			maxDiameter = Math.min(freeHspace, freeVspace),
			centerX = width/2,
			centerY = freeVspace/2 + self._padding,
			innerCircleRadius = 50,
			radiusIncrement = (maxDiameter/2 - innerCircleRadius) / numLevels;

		d3.select(container).select('svg')
			.attr('width', width)
			.attr('height', height);

		renderInnerCircle(data.all.length, centerX, centerY, innerCircleRadius, container)
	}

	function _render(width, height, data, numLevels, levels, container){
		//console.log(width, height, data, numLevels, levels, container)
		setupColorSchemes();
		renderSunburst(width, height, data, numLevels, levels, container);
	}

	return _init();
};