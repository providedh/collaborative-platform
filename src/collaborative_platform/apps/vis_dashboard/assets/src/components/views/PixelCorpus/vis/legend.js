import * as _d3 from 'd3';
import d3_legend from 'd3-svg-legend';
const d3 = Object.assign(_d3, d3_legend);

export default function renderLegend(svg, legendWidth, padding, entityColorScale, certaintyColorScale, colorCertaintyBy){
	const {width, height} = svg.getBoundingClientRect();

	console.log(certaintyColorScale)

	const tempScale = d3.scaleThreshold()
	  .domain([0, 5, 10, 15, 20 ])
	  .range(d3.range(5).map(x=>certaintyColorScale(x/5)));

	const entityLegend = d3.legendColor()
		.title('Entities')
  		.shape("path", d3.symbol().type(d3.symbolSquare).size(150)())
  		.shapePadding(0)
		.scale(entityColorScale);

	const certaintyLegend = d3.legendColor()
		.title(colorCertaintyBy)
		.scale(tempScale)//certaintyColorScale);

  	d3.select(svg)
  		.select('.entityLegend')
  		.call(entityLegend)
  		.transition()
  			.attr("transform", `translate(${width - legendWidth - padding}, ${padding*3})`);

  	d3.select(svg)
  		.select('.certaintyLegend')
  		.call(certaintyLegend)
  		.transition()
  			.attr("transform", `translate(${width - legendWidth - padding}, ${(height - padding)/2})`);
}