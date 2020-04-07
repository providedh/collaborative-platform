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

	function _setupColorSchemes(){
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

	function _renderLegend(width, height, levels, container){

	}

	function _renderInnerCircle(annotationsCount, centerX, centerY, innerCircleRadius, container){
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

	function _partition(data, radius){
		window.d3 = d3;
		console.log(data)
		return d3.partition().size([2 * Math.PI, radius])
			(d3.hierarchy(data, d=>d.value).sum(d => 1))
		//	    .sort((a, b) => b.value - a.value))
	}

	function _renderSections(data, count, levels, container, maxDiameter, centerX, centerY){
		const root = _partition(data, maxDiameter/2);
		root.each(d => d.current = d);

		const arc = d3.arc()
		    .startAngle(d => d.x0)
		    .endAngle(d => d.x1)
		    .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
		    .padRadius(maxDiameter / 4)
		    .innerRadius(d => d.y0)
		    .outerRadius(d => d.y1 - 1)

		const g = d3.select(container).select('g.sections')
			.attr('transform', `translate(${centerX}, ${centerY})`);

		//console.log(data)
		//console.log(root, arc)
	}

	function _setupHoverTooltip(){
	}

	function _renderSunburst(data, count, levels, container){
		const numLevels = Object.keys(levels).length,
			height = container.clientHeight,
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


		_renderInnerCircle(count, centerX, centerY, innerCircleRadius, container);
		_renderSections(data, count, levels, container, maxDiameter, centerX, centerY);
	}

	function _render(data, count, levels, container){
		//console.log(data)
		_setupColorSchemes();
		_renderSunburst(data.all, count, levels, container);
	}

	return _init();
};