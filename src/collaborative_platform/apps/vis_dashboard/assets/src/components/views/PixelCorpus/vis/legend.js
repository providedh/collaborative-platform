import * as _d3 from 'd3';
import d3_legend from 'd3-svg-legend';
const d3 = Object.assign(_d3, d3_legend);

export default function renderLegend(svg, legendWidth, padding, entityColorScale, certaintyColorScale, colorCertaintyBy){
	const {width, height} = svg.getBoundingClientRect();

	const tempScale = d3.scaleThreshold()
	  .domain([ 0, 1000, 2500, 5000, 10000 ])
	  .range(d3.range(6)
	  .map(function(i) { return "q" + i + "-9"}));

	const entityLegend = d3.legendColor()
		.title('Entities')
  		.shape("path", d3.symbol().type(d3.symbolSquare).size(150)())
  		.shapePadding(10)
		.scale(entityColorScale);

	const certaintyLegend = d3.legendColor()
		.title(colorCertaintyBy)
		.scale(tempScale)//certaintyColorScale);

  	d3.select(svg)
  		.select('.entityLegend')
  		.call(entityLegend)
  		.transition()
  			.attr("transform", `translate(${width - legendWidth - padding}, ${padding})`);

  	d3.select(svg)
  		.select('.certaintyLegend')
  		.call(certaintyLegend)
  		.transition()
  			.attr("transform", `translate(${width - legendWidth - padding}, ${(height - 2*padding)/2})`);
}