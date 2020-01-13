import * as d3 from 'd3';

function createScales(data, barDirection, height, width, padding=10, fontSize=12){
    let scales = {xScale:null, yScale: null};

    const dimensions = Object.keys(data[0]),
        [xDim, yDim] = barDirection=='Vertical'?dimensions:[dimensions[1], dimensions[0]];

    const [xTickLength, yTickLength] = [
        Math.max(...data.map(x=>String(x[xDim]).length)),
        Math.max(...data.map(x=>String(x[yDim]).length))
        ]

    const paddingLeft = padding + yTickLength*8,
        paddingBottom = padding + fontSize + 2,
        paddingRight = padding + xDim.length*8,
        paddingTop = padding + fontSize + 2;
        
    const scaleWidth = width - paddingRight - paddingLeft,
        scaleHeight = height - paddingTop - paddingBottom;

    const xData = data.map(d=>d[xDim]),
        yData = data.map(d=>d[yDim]);

    const xDomain = barDirection=='Vertical'?xData:[0, Math.max(...xData) + 10],
        yDomain = barDirection=='Vertical'?[0, Math.max(...yData) + 10]:yData;

    const xScale = barDirection=='Vertical'?d3.scaleBand().padding(0.1):d3.scaleLinear(),
        yScale = barDirection=='Vertical'?d3.scaleLinear():d3.scaleBand().padding(0.1);

    xScale.rangeRound([0, scaleWidth]).domain(xDomain);
    yScale.rangeRound([scaleHeight, 0]).domain(yDomain);

    return {xScale, yScale, left:paddingLeft, bottom:paddingBottom, right:paddingRight, top:paddingTop, margin:padding};
}

function renderHorizontalAxis(data, context, xScale, width, height, padding, barDirection, tickCount=10, tickSize=5){
    const label = barDirection=='Vertical'?Object.keys(data[0])[0]:Object.keys(data[0])[1];

    context.save();
    context.strokeStyle = 'slategrey';
    context.fillStyle = 'rgb(33, 37, 41)';
    context.textAlign = "center";
    context.textBaseline = "top";

    context.moveTo(padding.left, height - padding.bottom);
    context.lineTo(width - padding.margin, height - padding.bottom);
    context.stroke();

    context.moveTo(padding.left, height - padding.bottom);
    context.lineTo(padding.left, height - padding.bottom + tickSize);
    context.stroke();

    if(barDirection=='Vertical') {
        xScale.domain().forEach(d=>{
            context.moveTo(padding.left + xScale(d) + xScale.bandwidth()/2, height - padding.bottom);
            context.lineTo(padding.left + xScale(d) + xScale.bandwidth()/2, height - padding.bottom + tickSize);
            context.fillText(d, padding.left + xScale(d) + xScale.bandwidth()/2, height - padding.bottom + tickSize + 2);
            context.stroke();
        });
    } else {
        xScale.ticks(tickCount).forEach(d=>{
            context.moveTo(padding.left + xScale(d), height - padding.bottom);
            context.lineTo(padding.left + xScale(d), height - padding.bottom + tickSize);
            context.fillText(d, padding.left + xScale(d), height - padding.bottom + tickSize + 2);
            context.stroke();
        });
    }

    context.textBaseline = "bottom";
    context.textAlign = "end";
    context.fillText(label, width - padding.margin, height - padding.bottom - 2);

    context.restore()
}

function renderVerticalAxis(data, context, yScale, width, height, padding, barDirection, tickCount=10, tickSize=5){
    const label = barDirection=='Vertical'?Object.keys(data[0])[1]:Object.keys(data[0])[0];

    context.save();
    context.strokeStyle = 'slategrey';
    context.fillStyle = 'rgb(33, 37, 41)';
    context.textAlign = "end";
    context.textBaseline = "middle";

    context.moveTo(padding.left, padding.margin);
    context.lineTo(padding.left, height - padding.bottom);
    context.stroke();

    context.moveTo(padding.left, height - padding.bottom);
    context.lineTo(padding.left - tickSize, height - padding.bottom);
    context.stroke();

    if(barDirection=='Vertical') {
        yScale.ticks(tickCount).forEach(d=>{
            context.moveTo(padding.left, yScale(d) + padding.top);
            context.lineTo(padding.left - tickSize, yScale(d) + padding.top);
            context.fillText(d, padding.left - tickSize - 2, yScale(d) + padding.top);
            context.stroke();
        });
    } else {
        yScale.domain().forEach(d=>{
            context.moveTo(padding.left, yScale(d) + yScale.bandwidth()/2 + padding.top);
            context.lineTo(padding.left - tickSize, yScale(d) + yScale.bandwidth()/2 + padding.top);
            context.fillText(d, padding.left - tickSize - 2, yScale(d) + yScale.bandwidth()/2 + padding.top);
            context.stroke();
        });
    }

    context.textAlign = "start";
    context.textBaseline = "top";
    context.fillText(label, padding.left + 8, padding.margin);

    context.restore()
}

function barFactory(barDirection){
    if (barDirection == 'Vertical') {
        return renderVerticalBars
    } else {
        return renderHorizontalBars
    }
}

function renderVerticalBars(data, context, xScale, yScale, width, height, padding){
    const [xDim, yDim] = Object.keys(data[0]);

    function renderBar(bar_data){
        const y = yScale(bar_data[yDim]),
            box = [
                padding.left + xScale(bar_data[xDim]),
                y + padding.top,
                xScale.bandwidth(),
                height - y - padding.bottom - padding.top
            ];
        
        context.fillRect(...box)
        return box;
    }

    context.save();
    context.fillStyle = '#007bff';
    const rendered = data.map(d=>({box:renderBar(d), data:Object.values(d)}));
    context.restore();

    return rendered;
}

function renderHorizontalBars(data, context, xScale, yScale, width, height, padding){
    const [yDim, xDim] = Object.keys(data[0]);

    function renderBar(bar_data){
        const x = xScale(bar_data[yDim]),
            box = [
                padding.left,
                yScale(bar_data[yDim]) + padding.top,
                xScale(bar_data[xDim]),
                yScale.bandwidth()
            ];

        context.fillRect(...box);
        return box;
    }

    context.save();
    context.fillStyle = '#007bff';
    const rendered = data.map(d=>({box:renderBar(d), data:Object.values(d)}));
    context.restore();

    return rendered;
}

function overlayFactory(barDirection){
    if (barDirection == 'Vertical') {
        return renderVerticalOverlay
    } else {
        return renderHorizontalOverlay
    }
}

function renderVerticalOverlay(data, context, xScale, yScale, width, height, padding){
    const [xDim, yDim] = Object.keys(data[0]);

    const fillColorScale = d3.scaleOrdinal()
        .range(d3.schemeTableau10);

    function renderBar(bar_data){
        let y = height - padding.bottom;
        const x = padding.left + xScale(bar_data[xDim]);

        const rendered = Object.entries(bar_data[yDim]).map(d=>{
            context.fillStyle = fillColorScale(d[0]);
            const barHeight = height - padding.bottom - padding.top - yScale(d[1]),
                box = [x, y - barHeight, xScale.bandwidth(), barHeight]

            context.fillRect(...box);
            y -= barHeight;

            return {box, data:d}
        })

        return rendered;
    }

    context.save();
    const rendered = data.map(d=>renderBar(d)).flat();

    context.restore();
    return rendered;
}

function renderHorizontalOverlay(data, context, xScale, yScale, width, height, padding){
    const [yDim, xDim] = Object.keys(data[0]);

    const fillColorScale = d3.scaleOrdinal()
        .range(d3.schemeTableau10);

    function renderBar(bar_data){
        let x = padding.left;
        const y = yScale(bar_data[yDim]) + padding.top;

        const rendered = Object.entries(bar_data[xDim]).map(d=>{
            context.fillStyle = fillColorScale(d[0]);
            const barWidth = xScale(d[1]),
                box = [x, y, barWidth, yScale.bandwidth()];

            context.fillRect(...box);
            x += barWidth;

            return {box, data:d}
        })

        return rendered;
    }

    context.save();
    const rendered = data.map(d=>renderBar(d)).flat();

    context.restore();
    return rendered;
}

function setupInteractions(renderedData, overlayCanvas, ){
    const context = overlayCanvas.getContext("2d");
    
    const renderedDataSorted = renderedData.sort(
        (d0, d1)=>(
            (d0.box[1] < d1.box[1]) || // higher
            (d0.box[1] == d1.box[1] && d0.box[0] < d1.box[0]))?-1:1); // to the right

    function handleOverlayHover(e){
        const [x, y] = d3.mouse(this);

        let temp = null, node = null;
        let index = 0;
        do{
            temp = renderedData[index++];
            if(temp.box[0] < x && x < (temp.box[0] + temp.box[2]) &&
                    temp.box[1] < y && y < (temp.box[1] + temp.box[3])){
                node = temp;
            }
        }while(node == null && index < renderedData.length);

        context.clearRect(0,0,overlayCanvas.width, overlayCanvas.height);
        if(node != null){
            const label = `${node.data[1]} ${node.data[0]}`;
            context.save()
            context.fillStyle = '#f8f9fa';
            context.strokeStyle = '#00b3b0';
            context.beginPath();
            context.rect(x+5, y-10, label.length*6+5,20)
            context.stroke();
            context.fill();
            context.closePath();
            context.textBaseline = 'bottom';
            context.fillStyle = '#00b3b0';
            context.fillText(label,x+10, y+5)
            context.restore()
        }
    }

    d3.select(overlayCanvas)
        .on('mousemove', handleOverlayHover);
}

export default function render(container, canvas, overlayCanvas, data, overlay_data, render_overlay, barDirection){
	if(container == null || canvas == null || data == null)
		return

    const dimensions = Object.keys(data[0]);

	canvas.width = container.clientWidth;
	canvas.height = container.clientHeight;
    overlayCanvas.width = container.clientWidth;
    overlayCanvas.height = container.clientHeight;
	
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);

    const {xScale, yScale, ...padding} = createScales(data, barDirection, canvas.height, canvas.width);
    const renderData = barFactory(barDirection);
    const renderOverlay = overlayFactory(barDirection);

    let renderedData = renderData(data, context, xScale, yScale, canvas.width, canvas.height, padding);
    if(render_overlay === true)
        renderedData = renderOverlay(overlay_data, context, xScale, yScale, canvas.width, canvas.height, padding);

    setupInteractions(renderedData, overlayCanvas);

    renderHorizontalAxis(data, context, xScale, canvas.width, canvas.height, padding, barDirection);
    renderVerticalAxis(data, context, yScale, canvas.width, canvas.height, padding, barDirection);

}