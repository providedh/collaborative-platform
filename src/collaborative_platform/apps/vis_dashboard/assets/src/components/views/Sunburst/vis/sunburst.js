import * as d3_ from 'd3';
import * as d3Legend from 'd3-svg-legend';
const d3 = Object.assign({}, d3_, d3Legend)

/* Class: Heatmap
 *
 * 
 * */
export default function Sunburst(){
	const self = {
		_eventCallback: null,
		_padding: 10,
		_legendWidth: 120,
		_hoverTooltipHeight: 10,
		_extraVspacing: 50,
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
			default: null,
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

	function _renderLegend(container, x, y){
		const legend = d3.select(container).select('g.legend'),
			legendNode = legend.node(),
			labels = self._colorSchemes.default.domain().map(x => _shorttenedLabel(x+'')),
			maxLabelLength = labels.reduce((max, x)=>max>x.length?max:x.length, 0);

		const legendOrdinal = d3.legendColor()
		  .orient('horizontal')
		  .shape('path', d3.symbol().type('rect'))
		  .shapeWidth(maxLabelLength*6)
		  .shapePadding(10)
		  .labelAlign('middle')
		  .cellFilter(function(d){ return d.label !== 'e' })
		  .labels(labels)
		  .scale(self._colorSchemes.default);

		legend.call(legendOrdinal);
		const {width, height} = legendNode.getBBox()
		d3.select(container).select('g.legend')
			.attr('transform', `translate(${x - width/2}, ${y - height - self._padding})`);
	}

	function _renderInnerCircle(annotationsCount, centerX, centerY, innerCircleRadius, container){
		d3.select(container).select('svg').selectAll('g.innerCircle')
			.data([annotationsCount])
			.enter().append('svg:g')
			.attr('class', 'innerCircle')
			.each(function(d){
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
				//d3.select(this)
				//	.append('svg:circle')
				//	.attr('r', innerCircleRadius)
				//	.attr('cx', innerCircleRadius)
				//	.attr('cy', innerCircleRadius);
			})

		d3.select(container).select('svg').selectAll('g.innerCircle')
			.attr('transform', `translate(${centerX - innerCircleRadius}, ${centerY - innerCircleRadius})`)
			.each(function(d){
				d3.select(this).select('text.annotations').text(d);
			})
	}

	function _partition(data, radius){
		return d3.partition().size([2 * Math.PI, radius])
			(d3.hierarchy(data, d=>d.children).sum(d => 1))
		//	    .sort((a, b) => b.value - a.value))
	}

	function _shorttenedLabel(label, maxLabelLength = 16){
		if(label.length <= maxLabelLength)
			return label;

		const overflow = label.length - maxLabelLength,
			fragmentLength = Math.trunc(maxLabelLength/2 - 2),
			startFragment = label.slice(0, fragmentLength),
			endFragment = label.slice(label.length - fragmentLength, label.length);
		return startFragment + '...' + endFragment;
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
		
		g.select('g.paths')
      		.attr('fill-opacity', 0.6)
    		.selectAll('path')
    		.data(root.descendants().filter(d=>(d.depth && d.depth <= Object.keys(levels).length)))
    		.join('path')
      			.attr('fill', d => { while (d.depth > 1) d = d.parent; return self._colorSchemes.default(d.data.name); })
      			.attr('d', arc)
    			//.append('title')
      			//	.text(d => `${d.ancestors().map(d => d.data.name).reverse().join('/')}\n${format(d.value)}`);

  		g.select('g.labels')
    		.selectAll('text')
    			.data(root.descendants().filter(d => d.depth && (d.y0 + d.y1) / 2 * (d.x1 - d.x0) > 10))
    			.join('text')
      			.attr('transform', function(d) {
        			const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
        			const y = (d.y0 + d.y1) / 2;
        			return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
      			})
      			.attr('dy', '0.35em')
      			.text(d => _shorttenedLabel(d.data.name+''));
	}

	function _setupHoverTooltip(container, x, y){
		d3.select(container).select('g.hovertooltip')
			.attr('transform', `translate(${x}, ${y + self._hoverTooltipHeight - self._extraVspacing})`);

		d3.select(container).select('g.paths').selectAll('path')
			.on('mouseenter', d=>{
				let hierarchy = [d.data.name], t = d;
				while(t = t?.parent) hierarchy = [t.data.name, ...hierarchy];

				// remove the 'root' label
				hierarchy.shift();

				d3.select(container).select('g.hovertooltip text')
					.text(`${hierarchy.join(' > ')} (${d.value} annotations)`);
			})
			.on('mouseleave', d=>{
				d3.select(container).select('g.hovertooltip text').text('');
			})
	}

	function _renderSunburst(data, count, levels, container){
		const numLevels = Object.keys(levels).length,
			height = container.clientHeight,
			width = container.clientWidth,
			freeVspace = height - (self._padding*2 + self._hoverTooltipHeight),
			freeHspace = width - (self._padding * 2),
			maxDiameter = Math.min(freeHspace, freeVspace) + self._extraVspacing,
			centerX = width/2,
			centerY = freeVspace/2 + self._padding - self._extraVspacing,
			innerCircleRadius = 50;

		self._colorSchemes.default = d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, data.children.length + 1));

		d3.select(container).select('svg')
			.attr('width', width)
			.attr('height', height);

		_renderInnerCircle(count, centerX, centerY, innerCircleRadius, container);
		_renderSections(data, count, levels, container, maxDiameter, centerX, centerY);
		_setupHoverTooltip(container, centerX, centerY+maxDiameter/2);
		_renderLegend(container, centerX, height);
	}

	function _render(data, count, levels, container){
		//console.log(data)
		_setupColorSchemes();
		_renderSunburst(data.all, count, levels, container);
	}

	return _init();
};