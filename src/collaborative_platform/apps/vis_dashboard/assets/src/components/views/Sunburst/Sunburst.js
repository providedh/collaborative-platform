import React, { useEffect, useState, useRef } from "react";

import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';
import {useRender} from './vis';
import {DataClient} from '../../../data';

function useData(dataClient, source){
    const [data, setData] = useState(null);

    useEffect(()=>{
        dataClient.unsubscribe('entity');
        dataClient.unsubscribe('certainty');
        dataClient.unsubscribe('meta');

        dataClient.subscribe(source, data=>{
            setData(data);
        });
    }, [source])

    return data;
}

function handleFilter([min, max], data, dataClient){
    function inRange(entry){
        
    }
}

function Sunburst ({ layout, source, numberOfLevels, ...levels}) {
	const containerRef = useRef();
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
	const data = useData(dataClient, source);
    
    useRender(width, height, data, numberOfLevels, levels, containerRef)

    return(
        <div className={styles.sunburst} ref={containerRef}>
            <svg/>
        </div>
    )
}

Sunburst.prototype.description = "Arrange entities and annotations in a circular layout"+
    "to discover trends and outliers."

Sunburst.prototype.getConfigOptions = getConfig;

export default Sunburst;
