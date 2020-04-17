import React, { useEffect, useState, useRef } from "react";

import styles from './style.module.css';
import css from './style.css';
import dummy_data from './dummy_data';
import dummy_overlay from './overlay_data';
import render from './render';
import getConfig from './config';
import {DataClient, useCleanup} from '../../../data';

function useData(dataClient, dimension){
	const [data, setData] = useState(null);

	useEffect(()=>{
        if(dimension == 'Number of entities per type'){
            dataClient.unsubscribe('entity');
            dataClient.subscribe('entity', data=>{
                const count = {};
                data.filtered.forEach(x=>count.hasOwnProperty(x.type)?count[x.type]++:count[x.type]=1);
                const entries = Object.entries(count).map(x=>({type:x[0], count:x[1]}));
                setData(entries);
            });
        }else if(dimension == 'Most common entities'){
            dataClient.unsubscribe('entity');
            dataClient.subscribe('entity', data=>{
                const count = {};
                data.filtered.forEach(x=>count.hasOwnProperty(x.name)?count[x.name]++:count[x.name]=1);
                const entries = Object
                    .entries(count)
                    .map(x=>({name:x[0], count:x[1]}))
                    .sort((x,y)=>x.count-y.count);
                const mostCommon = [];

                for(let i=0; i<entries.length && i<5; i++)
                    mostCommon.push(entries.pop());
                if(entries.length > 0)
                    mostCommon.push({name:'other', count:entries.reduce((ac,dc)=>ac+dc.count, 0)});

                setData(mostCommon);
            });
        }else if(dimension == 'Number of entities per document'){
            dataClient.unsubscribe('entity');
            dataClient.subscribe('entity', data=>{
                const count = {};
                data.filtered.forEach(x=>count.hasOwnProperty(x.file_name)?count[x.file_name]++:count[x.file_name]=1);
                const entries = Object.entries(count).map(x=>({file_name:x[0], count:x[1]}));
                setData(entries);
            });
        }else{
            dataClient.unsubscribe('entity');
		    setData(dummy_data[dimension])
        }
	}, [dimension])

	return data;
}

function useOverlay(renderOverlay, dimension, overlay){
	const [overlayData, setOverlayData] = useState(dummy_overlay[overlay][dimension]);

	useEffect(()=>{
		setOverlayData(renderOverlay===true?dummy_overlay[overlay][dimension]:null)
	}, [renderOverlay, dimension, overlay])

	return overlayData;
}

function getOnEventCallback(dataClient, dimension, barDirection){
    return (event)=>{
        console.log(event);
    };
}

function Histogram({dimension, barDirection, renderOverlay, overlay, layout}) {
	const [refContainer, refCanvas, refOverlayCanvas] = [useRef(), useRef(), useRef()];
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
    useCleanup(dataClient);
	const data = useData(dataClient, dimension);
    const onEvent = getOnEventCallback(dataClient, dimension, barDirection);
	//const overlay_data = useOverlay(renderOverlay, dimension, overlay);

    useEffect(()=>render(
    		refContainer.current, 
    		refCanvas.current, 
    		refOverlayCanvas.current, 
    		data, 
    		null, 
    		renderOverlay, 
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
