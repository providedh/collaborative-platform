import React, { useEffect, useState, useRef } from "react";

import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';
import {RegularHeatmapBuilder, StairHeatmapBuilder, HeartHeatmapBuilder, Director} from './vis';
import {DataClient} from '../../../data';
import useData from './data';

function useHeatmap(layout, colorScale, rangeScale, eventCallback){
    const [heatmap, setHeatmap] = useState(null)
    useEffect(()=>{
        let builder = RegularHeatmapBuilder();
        if(layout == 'Split')
            builder = StairHeatmapBuilder();
        if(layout == 'Tilted')
            builder = HeartHeatmapBuilder();

        const director = Director(builder);
        director.make(colorScale, rangeScale, eventCallback);
        setHeatmap(builder.getResult())
    }, [layout, colorScale, rangeScale])

    return heatmap;
}

function useRender(width, height, heatmap, data, containerRef, canvasRef, overlayCanvasRef, legendRef){
    useEffect(()=>{
        if(heatmap != null)
            heatmap.render(data, containerRef.current, canvasRef.current, overlayCanvasRef.current, legendRef.current)
        }, // Render 
        [width, height, heatmap, data]); // Conditions*/
}

function handleFilter([min, max], data, dataClient){
    function inRange(entry){
        
    }
}

function Heatmap({ layout, tileLayout, colorScale, rangeScale, source, axis1, axis2}) {
	const [containerRef, canvasRef, overlayCanvasRef, legendRef] = [useRef(), useRef(), useRef(), useRef()];
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
	const data = useData(dataClient, source, axis1, axis2);
    const heatmap = useHeatmap(tileLayout, colorScale, rangeScale, event=>event);
    
    useRender(width, height, heatmap, data, containerRef, canvasRef, overlayCanvasRef, legendRef);

    return(
        <div className={styles.heatmap} ref={containerRef}>
	        <canvas ref={canvasRef} className={styles.canvas}/>
	        <canvas className={styles.overlayCanvas} ref={overlayCanvasRef}/>
            <svg ref={legendRef} className={styles.legendBrush}/>
        </div>
    )
}

Heatmap.prototype.description = "Examine multivariate data, relationship among data, and evolution through time in "+
    "a generalized manner user a color encoded grid array."

Heatmap.prototype.getConfigOptions = getConfig;

export default Heatmap;
