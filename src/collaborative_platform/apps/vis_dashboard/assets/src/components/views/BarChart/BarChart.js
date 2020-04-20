import React, { useEffect, useState, useRef } from "react";

import styles from './style.module.css';
import css from './style.css';
import render from './render';
import getConfig from './config';
import useData from './data';
import {DataClient, useCleanup} from '../../../data';
import getOnEventCallback from './event';

function BarChart({layout, dimension, barDirection}) {
	const [refContainer, refCanvas, refOverlayCanvas] = [useRef(), useRef(), useRef()];
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
    useCleanup(dataClient);
	const data = useData(dataClient, dimension);
    const onEvent = getOnEventCallback(dataClient, data?.filterDimension, data?.all);

    useEffect(()=>render(
		refContainer.current, 
		refCanvas.current, 
		refOverlayCanvas.current, 
		data,
		barDirection,
        onEvent), // Render 
	[width, height, barDirection, data]); // Conditions

    return(
        <div className={styles.histogram} ref={refContainer}>
	        <canvas ref={refCanvas}/>
	        <canvas className={styles.overlayCanvas} ref={refOverlayCanvas}/>
        </div>
    );
}

BarChart.prototype.description = "Encode frequencies using horizontal or vertical bars."

BarChart.prototype.getConfigOptions = getConfig;

export default BarChart;
