import * as d3 from 'd3';

import {BarChartDirection, BarChartDimension} from './config';


function createScales(data, barDirection, height, width, onEvent, padding=10, fontSize=12){
    const dimensions = [...data.all.keys()],
        maxTickLength = Math.max(...dimensions.map(x=>String(x).length)),
        maxCount = Math.max(...[...data.all.values()].map(x=>x.length)),
        labelTickSize = maxTickLength * (fontSize/2.2),
        countTickSize = String(maxCount).length * (fontSize/2.2),
        [xTickLength, yTickLength] = barDirection===BarChartDirection.horizontal
            ? [countTickSize, labelTickSize]
            : [labelTickSize, countTickSize],
        [xLabel, yLabel] = barDirection===BarChartDirection.horizontal
            ? ['count', data.dimension]
            : [data.dimension, 'count'];

    const paddingLeft = padding*2 + yTickLength,
        paddingBottom = padding + fontSize + 2,
        paddingRight = padding + xTickLength + xLabel.length*(fontSize/2.2),
        paddingTop = padding*2 + fontSize + 2;
        
    const scaleWidth = width - paddingRight - paddingLeft,
        scaleHeight = height - paddingTop - paddingBottom;

    const [xDomain, yDomain] = barDirection==BarChartDirection.horizontal
        ? [[0, maxCount], dimensions]
        : [dimensions, [0, maxCount]];

    const [xScale, yScale] = barDirection==BarChartDirection.horizontal
        ? [d3.scaleLinear(), d3.scaleBand().padding(0.1)]
        : [d3.scaleBand().padding(0.1), d3.scaleLinear()];

    xScale.rangeRound([0, scaleWidth]).domain(xDomain);
    yScale.rangeRound([scaleHeight, 0]).domain(yDomain);

    return {xScale, yScale, left:paddingLeft, bottom:paddingBottom, right:paddingRight, top:paddingTop, margin:padding};
}

function renderHorizontalAxis(data, context, xScale, width, height, padding, barDirection, tickCount=10, tickSize=5){
    const label = barDirection===BarChartDirection.horizontal?'count':data.dimension;

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

    if(barDirection === BarChartDirection.vertical) {
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
    const label = barDirection===BarChartDirection.vertical?'count':data.dimension;

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
    const createBarBox = barDirection === BarChartDirection.vertical
        ? createVerticalBarBox
        : createHorizontalBarBox;

    return (data, context, xScale, yScale, padding)=>renderBars(data, context, xScale, yScale, padding, createBarBox);
}

function renderBars(data, context, xScale, yScale, padding, createBarBox){
    context.save();

    context.fillStyle = 'lightgrey';

    const rendered = [...data.all.entries()].map(([label, items])=>{
        const box = createBarBox(label, items, xScale, yScale, padding);
        context.fillRect(...box);

        return {box, data: [label, items.length]};
    });

    context.fillStyle = '#007bff';
    [...data.filtered.entries()].forEach(([label, items])=>{
        const box = createBarBox(label, items, xScale, yScale, padding);
        context.fillRect(...box);
    });

    context.restore();

    return rendered;
}

function createVerticalBarBox(label, items, xScale, yScale, padding){
    const y = yScale(items.length),
        box = [
            padding.left + xScale(label),
            y + padding.top,
            xScale.bandwidth(),
            yScale.range()[0] - y
        ];
    
    return box;
}

function createHorizontalBarBox(label, items, xScale, yScale, padding){
    const box = [
        padding.left,
        yScale(label) + padding.top,
        xScale(items.length),
        yScale.bandwidth()
    ];

    return box;
}

function overlayFactory(barDirection){
    if (barDirection === BarChartDirection.vertical) {
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

function setupInteractions(renderedData, overlayCanvas, onEvent){
    const context = overlayCanvas.getContext("2d");
    
    const renderedDataSorted = renderedData.sort(
        (d0, d1)=>(
            (d0.box[1] < d1.box[1]) || // higher
            (d0.box[1] == d1.box[1] && d0.box[0] < d1.box[0]))?-1:1); // to the right

    function pointInside(x,y, box){
        return (box[0] < x 
            && x < (box[0] + box[2]) 
            && box[1] < y 
            && y < (box[1] + box[3])
        );
    }

    function getEventTarget([x, y]){
        let temp = null, node = null;
        let index = 0;
        do{
            temp = renderedData[index++];
            if(pointInside(x,y,temp.box)){
                node = temp;
            }
        }while(node == null && index < renderedData.length);

        return {node, index};
    }

    function updateTooltip([x, y], node){
        if(node != null){
            const label = `${node.data[0]}  (${node.data[1]})`;
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

    function handleHover(){
        const eventPosition = d3.mouse(this),
            {node, index} = getEventTarget(eventPosition);
        context.clearRect(0,0,overlayCanvas.width, overlayCanvas.height);

        if(node != null){
            updateTooltip(eventPosition, node);
            onEvent({source:'hover', target: node});
        }
    }

    function handleClick(){
        const eventPosition = d3.mouse(this),
            {node, index} = getEventTarget(eventPosition);

        if(node != null){
            onEvent({source:'click', target: node});
        }
    }

    d3.select(overlayCanvas)
        .on('mousemove', handleHover)
        .on('click', handleClick);
}

export default function render(container, canvas, overlayCanvas, data, barDirection, onEvent){
    //console.log(container, canvas, data, data?.filtered?.size)
	if(container == null || canvas == null || data == null || data.filtered.size == 0)
		return

    const dimensions = [...data.all.keys()];

	canvas.width = container.clientWidth;
	canvas.height = container.clientHeight;
    overlayCanvas.width = container.clientWidth;
    overlayCanvas.height = container.clientHeight;
	
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);

    const {xScale, yScale, ...padding} = createScales(data, barDirection, canvas.height, canvas.width);
    const renderData = barFactory(barDirection);
//    const renderOverlay = overlayFactory(barDirection);
//
    let renderedData = renderData(data, context, xScale, yScale, padding);
//    if(render_overlay === true)
//        renderedData = renderOverlay(overlay_data, context, xScale, yScale, canvas.width, canvas.height, padding);
//
    setupInteractions(renderedData, overlayCanvas, onEvent);
//
    renderHorizontalAxis(data, context, xScale, canvas.width, canvas.height, padding, barDirection);
    renderVerticalAxis(data, context, yScale, canvas.width, canvas.height, padding, barDirection);

}