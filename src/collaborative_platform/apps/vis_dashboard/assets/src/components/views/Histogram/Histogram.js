import React, { useEffect, useState, useRef } from "react";
import styles from './style.module.css';
import css from './style.css';
import dummy_data from './dummy_data';
import dummy_overlay from './overlay_data';
import render from './vis';


function useData(dimension){
	const [data, setData] = useState(dummy_data[dimension]);

	useEffect(()=>{
		setData(dummy_data[dimension])
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

function Histogram({dimension, barDirection, renderOverlay, overlay, layout}) {
	const [refContainer, refCanvas, refOverlayCanvas] = [useRef(), useRef(), useRef()];
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

	const data = useData(dimension);
	const overlay_data = useOverlay(renderOverlay, dimension, overlay);

    useEffect(()=>render(
    		refContainer.current, 
    		refCanvas.current, 
    		refOverlayCanvas.current, 
    		data, 
    		overlay_data, 
    		renderOverlay, 
    		barDirection), // Render 
    	[width, height, barDirection, data, overlay_data]); // Conditions

    return(
        <div className={styles.histogram} ref={refContainer}>
	        <canvas ref={refCanvas}/>
	        <canvas className={styles.overlayCanvas} ref={refOverlayCanvas}/>
        </div>
    )
}

Histogram.prototype.description = "Encode frequencies using horizontal or vertical bars."

Histogram.prototype.configOptions = [
    {name: 'barDirection', type: 'selection', value: 'Horizontal', params: {
    	options: [
    		'Horizontal',
    		'Vertical'
    	]}
    },
    {name: 'dimension', type: 'selection', value: 'entityType', params: {
    	options: [
	    	'Number of entities per document',
	    	'Number of entities per type',
	    	'Number of annotations per document',
	    	'Number of annotations per category',
	    	"Frequency for an attribute's values",
	    	'Frequency for most common attribute values',
    	]}
    },
    {name: 'renderOverlay', type: 'toogle', value: false},
    {name: 'overlay', type: 'selection', value: 'Certainty level', params: {
    	options: [
    		'Certainty level',
    		'Author',
    		'Time of last edit'
    	]}
    },
];

export default Histogram;
