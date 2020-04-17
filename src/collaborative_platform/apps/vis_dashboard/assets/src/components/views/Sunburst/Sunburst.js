import React, { useEffect, useState, useRef } from "react";

import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';
import {useRender} from './vis';
import {DataClient} from '../../../data';
import useData from './data';

function onEvent(source, levels, event, dataClient, context){
        //console.log(source, levels['level'+event.depth], event.data)
    if(event.action === 'click'){
        if(levels['level'+event.depth] === 'file'){
            dataClient.filter('fileId', x=>x===(+event.data.name));
        }else if(levels['level'+event.depth] === 'file_name'){
            if(context.name2document.hasOwnProperty(event.data.name))
                dataClient.filter('fileId', x=>x===context.name2document[event.data.name]);
        }else{
            if(source === 'certainty'){
                const option2dimension = {
                    category: 'certaintyCategory',
                    degree: 'certaintyDegree',
                    cert: 'certaintyCert',
                    match: 'certaintyMatch',
                    resp: 'certaintyAuthor',
                };
                const dimension = option2dimension[levels['level'+event.depth]];

                if(dimension === 'certaintyCategory'){
                    dataClient.filter(dimension, x=>x.includes(event.data.name));
                }else{
                    dataClient.filter(dimension, x=>x===event.data.name);
                }
            }
        }
    }else{
        if(levels['level'+event.depth] === 'file'){
            dataClient.focusDocument(event.data.name);
        }else if(levels['level'+event.depth] === 'file_name'){
            dataClient.focusDocument(context.name2document[event.data.name]);
        }
    }
}

// ...rest has both the levels and the injected context prop
function Sunburst ({ layout, source, numberOfLevels, ...rest}) {
	const containerRef = useRef();
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];
    const {context} = rest;
    const levels = Object.fromEntries(
        Object.entries(rest).filter(([key, value])=>key.startsWith('level'))
    );

    const [dataClient, _] = useState(DataClient());
	const data = useData(dataClient, source, levels);

    useRender(width, height, data, source, levels, context.taxonomy, containerRef, (e)=>onEvent(source,levels, e, dataClient));

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
