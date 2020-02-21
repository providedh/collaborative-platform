import React, { useEffect, useState, useRef } from "react";
import styles from './style.module.css';
import css from './style.css';
import {RegularHeatmapBuilder, StairHeatmapBuilder, HeartHeatmapBuilder, Director} from './vis';
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

function useRender(width, height, heatmap, data, refContainer, refCanvas, refOverlayCanvas){
    useEffect(()=>{
        if(heatmap != null)
            heatmap.render(data, refContainer, refCanvas, refOverlayCanvas)
        }, // Render 
        [width, height, heatmap, data]); // Conditions*/
}

function Heatmap({ layout, tileLayout, colorScale, rangeScale, dimension}) {
	const [refContainer, refCanvas, refOverlayCanvas] = [useRef(), useRef(), useRef()];
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
	const data = useData(dataClient, dimension);
    const heatmap = useHeatmap(tileLayout, colorScale, rangeScale, event=>console.log(event));
    
    useRender(width, height, heatmap, data, refContainer, refCanvas, refOverlayCanvas);

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
    {name: 'tileLayout', type: 'selection', value: 'Regular', params: {
    	options: [
    		'Regular',
    		'Split',
            'Tilted',
    	]}
    },
    {name: 'colorScale', type: 'selection', value: 'Red and blue', params: {
    	options: [
    		'Red and blue',
    		'Spectral',
    		'Blues'
    	]}
    },
    {name: 'rangeScale', type: 'selection', value: 'Linear', params: {
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
