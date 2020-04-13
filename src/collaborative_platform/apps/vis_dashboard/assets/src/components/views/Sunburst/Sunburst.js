import React, { useEffect, useState, useRef } from "react";

import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';
import {useRender} from './vis';
import {DataClient} from '../../../data';
import useData from './data';

function onEvent(source, levels, event){
    console.log(source, levels['level'+event.depth], event.data)
}

function Sunburst ({ layout, source, numberOfLevels, ...levels}) {
	const containerRef = useRef();
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
	const {data, count} = useData(dataClient, source, levels);

    useRender(width, height, data, count, source, levels, containerRef, (e)=>onEvent(source,levels, e));

    return(
        <div className={styles.sunburst + ' sunburst'} ref={containerRef}>
            <svg>
            <g className='sections'>
                <g className='paths'></g>
                <g className={styles.labels + ' labels'}></g>
            </g>
            <g className={styles.hovertooltip + ' hovertooltip'}>
                <text></text>
            </g>
            <g className={styles.legend + ' legend'}></g>
            </svg>
        </div>
    )
}

Sunburst.prototype.description = "Arrange entities and annotations in a circular layout"+
    "to discover trends and outliers."

Sunburst.prototype.getConfigOptions = getConfig;

export default Sunburst;
