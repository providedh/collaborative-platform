import React, { useEffect, useState, useRef } from "react";
import styles from './style.module.css';
import css from './style.css';
import render from './vis';

import {DataClient} from '../../../data';

function useData(dataClient, dimension){
	const [data, setData] = useState(null);

	useEffect(()=>{
        if(dimension == 'Entities related by documents'){
            dataClient.unsubscribe('entity');
            dataClient.subscribe('entity', data=>{
                if(data == null || data.all.length == 0 || data.filtered.length == 0)
                    return 0;
                const entities = Array.from(new Set(data.filtered.map(x=>x.name)).values());

                const entitiesInDoc = {};
                data.filtered.forEach(x=>{
                    if(entitiesInDoc.hasOwnProperty(x.file_name)){
                        entitiesInDoc[x.file_name].add(x.name)
                    }else{
                        entitiesInDoc[x.file_name]=new Set([x.name])
                    }
                });

                const arrayOfEntities = ()=>entities.map(()=>[]);
                const concurrenceMatrix = {};
                entities.forEach(e=>concurrenceMatrix[e] = arrayOfEntities());

                for(let [doc, relatedEntities] of Object.entries(entitiesInDoc)){
                    const relatedEntitiesArray = Array.from(relatedEntities.values());
                    for(let entity of relatedEntitiesArray){
                        relatedEntitiesArray.forEach(e=>concurrenceMatrix[entity][entities.indexOf(e)].push(doc));
                    }
                }

                setData(concurrenceMatrix);
            });
        }else if(dimension == 'Documents related by entities'){
            dataClient.unsubscribe('entity');
            dataClient.subscribe('entity', data=>{
                if(data == null || data.all.length == 0 || data.filtered.length == 0)
                    return 0;
                const documents = Array.from(new Set(data.filtered.map(x=>x.file_name)).values());

                const entitiesInDoc = {};
                data.filtered.forEach(x=>{
                    if(entitiesInDoc.hasOwnProperty(x.name)){
                        entitiesInDoc[x.name].add(x.file_name)
                    }else{
                        entitiesInDoc[x.name]=new Set([x.file_name])
                    }
                });

                const arrayOfDocuments = ()=>documents.map(()=>[]);
                const concurrenceMatrix = {};
                documents.forEach(e=>concurrenceMatrix[e] = arrayOfDocuments());

                for(let [entity, relatedDocuments] of Object.entries(entitiesInDoc)){
                    const relatedDocumentsArray = Array.from(relatedDocuments.values());
                    for(let doc of relatedDocumentsArray){
                        relatedDocumentsArray.forEach(e=>concurrenceMatrix[doc][documents.indexOf(e)].push(entity));
                    }
                }

                setData(concurrenceMatrix);
            });
        }
	}, [dimension])

	return data;
}

function Heatmap({ layout, colorScale, numericalScale, dimension}) {
	const [refContainer, refCanvas, refOverlayCanvas] = [useRef(), useRef(), useRef()];
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
	const data = useData(dataClient, dimension);

    /*
    useEffect(()=>render(
    		refContainer.current, 
    		refCanvas.current, 
    		refOverlayCanvas.current, 
    		data, 
    		null, 
    		renderOverlay, 
    		barDirection), // Render 
    	[width, height, barDirection, data]); // Conditions*/

    return(
        <div className={styles.heatmap} ref={refContainer}>
	        <canvas ref={refCanvas}/>
	        <canvas className={styles.overlayCanvas} ref={refOverlayCanvas}/>
        </div>
    )
}

Heatmap.prototype.description = "Examine multivariate data, relationship among data, and evolution through time in "+
    "a generalized manner user a color encoded grid array."

Heatmap.prototype.configOptions = [
    {name: 'layout', type: 'selection', value: 'Regular', params: {
    	options: [
    		'Regular',
    		'Split',
            'Tilted',
    	]}
    },
    {name: 'colorScale', type: 'selection', value: 'Certainty level', params: {
    	options: [
    		'Certainty level',
    		'Author',
    		'Time of last edit'
    	]}
    },
    {name: 'numericalScale', type: 'selection', value: 'Linear', params: {
        options: [
            'Linear',
            'Logarithmic',
            'Power'
        ]}
    },
    {name: 'dimension', type: 'selection', value: 'Entities related by documents', params: {
    	options: [
	    	'Entities related by documents',
	    	'Documents related by entities',
    	]}
    },
];

export default Heatmap;
