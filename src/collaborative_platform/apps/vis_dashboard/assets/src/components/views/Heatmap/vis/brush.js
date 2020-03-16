import * as d3 from 'd3';

const margin = 2;

export default function setBrush(svg, x, y, width, height, onBrush){
	const brush = d3.brushY()
      .extent([[margin, margin], [width + margin, height + margin]])
      .on("start brush end", brushed);

	const legend = d3.select(svg)
		.style('left', (x-margin)+'px')
		.style('top', (y-margin)+'px')
		.attr('width', width + margin*2)
		.attr('height', height + margin*2)
      	.call(brush)
      	.call(brush.move, [0, height])
      	.call(g => g.select(".overlay")
          	.datum({type: "selection"})
          	.on("mousedown touchstart", beforebrushstarted));


  	function beforebrushstarted() {
    	const dx = x(1) - x(0); // Use a fixed width when recentering.
    	const [cx] = d3.mouse(this);
    	const [x0, x1] = [cx - dx / 2, cx + dx / 2];
    	const [X0, X1] = x.range();
    	d3.select(this.parentNode)
    	    .call(brush.move, x1 > X1 ? [X1 - dx, X1] 
    	        : x0 < X0 ? [X0, X0 + dx] 
    	        : [x0, x1]);
  	}

  	function brushed() {
    	const selection = d3.event.selection;
    	if (selection === null) {
      		onBrush(null);
    	} else {
	      	const [y0, y1] = selection;
	      	onBrush([y0, y1]);
    	}
  	}
}