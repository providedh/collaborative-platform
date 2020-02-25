import React, { useEffect, useState, useRef } from "react";
import styles from './style.module.css';
import css from './style.css';
import {DataClient} from '../../../data';
import getConfig from './config';

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

function DotMatrix({ layout, singleSource, dataSourceType, dataSource, dotType, colorBy}) {
	const [refContainer, refCanvas, refOverlayCanvas] = [useRef(), useRef(), useRef()];
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
	//const data = useData(dataClient, dimension);

    return(
        <div className={styles.dotMatrix} ref={refContainer}>
	        <canvas ref={refCanvas}/>
	        <canvas className={styles.overlayCanvas} ref={refOverlayCanvas}/>
        </div>
    )
}

DotMatrix.prototype.description = "Examine multivariate data, relationship among data, and evolution through time in "+
    "a generalized manner user a color encoded grid array."

DotMatrix.prototype.getConfigOptions = getConfig;

export default DotMatrix;
