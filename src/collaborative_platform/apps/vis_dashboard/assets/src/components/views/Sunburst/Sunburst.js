import React, { useEffect, useState, useRef } from "react";

import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';
import {useRender} from './vis';
import {DataClient} from '../../../data';
import useData from './data';

function onEvent(source, levels, event, dataClient){
        //console.log(source, levels['level'+event.depth], event.data)
    if(event.action === 'click'){
        if(levels['level'+event.depth] === 'file'){
            dataClient.filter('fileId', x=>x===(+event.data.name));
        }else if(levels['level'+event.depth] === 'file_name'){
        }
    }else{
        if(levels['level'+event.depth] === 'file'){
            dataClient.focusDocument(event.data.name);
        }else if(levels['level'+event.depth] === 'file_name'){
        }
    }
}

function Sunburst ({ layout, source, numberOfLevels, ...levels}) {
	const containerRef = useRef();
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
	const {data, count} = useData(dataClient, source, levels);

    useRender(width, height, data, count, source, levels, containerRef, (e)=>onEvent(source,levels, e, dataClient));

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
