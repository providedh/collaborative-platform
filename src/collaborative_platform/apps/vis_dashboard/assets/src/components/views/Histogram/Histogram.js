import React, { useEffect, useState, useRef } from "react";

import styles from './style.module.css';
import css from './style.css';
import render from './render';
import getConfig from './config';
import useData from './data';
import {DataClient, useCleanup} from '../../../data';


function getOnEventCallback(dataClient, dimension, data){
    if(!data)
        return null;

    return (({source, target})=>{
        if(source == 'click' && dimension != undefined){
            const [label, count] = target.data;
            if(dataClient.getFilters().includes(dimension)){
                const filter = dataClient.getFilter(dimension),
                    filterItems = [...data.keys()].filter(filter.filter);

                if(filterItems.includes(label)){ // remove item from filter
                    if(filterItems.length == 1)
                        dataClient.unfilter(dimension);
                    else{
                        filterItems.splice(filterItems.indexOf(label),1);
                        dataClient.filter(dimension, x=>filterItems.includes(x));
                    }
                }else{ // add items to filters
                    filterItems.push(label);
                    dataClient.filter(dimension, x=>filterItems.includes(x));
                }
            }else{
                dataClient.filter(dimension, x=>x===label);
            }
        }
    });
}

function Histogram({layout, dimension, barDirection}) {
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
    )
}

Histogram.prototype.description = "Encode frequencies using horizontal or vertical bars."

Histogram.prototype.getConfigOptions = getConfig;

export default Histogram;
