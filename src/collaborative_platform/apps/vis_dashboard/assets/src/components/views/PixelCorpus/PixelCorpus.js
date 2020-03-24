import React from 'react';
import {useState, useRef, useEffect} from 'react';

import {DataClient} from '../../../data';

import styles from './style.module.css';
import getConfig from './config';
import taxonomy from './taxonomy';
import {Vis} from './vis';

function useData(dataClient){
    const [data, setData] = useState({all: [], filtered: []});

    useEffect(()=>{
            dataClient.subscribe('entity', data=>{
                setData(data);
            })
    }, []);
        
    return data;
}

function useVis(sortDocumentsBy, colorCertaintyBy){
    const [vis, _] = useState(Vis());

    useEffect(()=>{ // Initialize vis component
        vis.setTaxonomy(taxonomy);
        vis.setDocSortingCriteria(sortDocumentsBy);
        vis.setEntitySortingCriteria(sortDocumentsBy);
        vis.setColorCertaintyBy(colorCertaintyBy);
        vis.setEventCallback(x=>console.log('event', x));
    }, []);

    vis.setDocSortingCriteria(sortDocumentsBy);
    vis.setColorCertaintyBy(colorCertaintyBy);

    return vis;
}

function PixelCorpus({sortDocumentsBy, colorCertaintyBy, layout}) {
    const [svgRef, containerRef] = [useRef(), useRef()];
    const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient()),
        data = useData(dataClient),
        vis = useVis(sortDocumentsBy, colorCertaintyBy);

    useEffect(()=>vis.render(
            containerRef.current,
            svgRef.current,
            data, data), // Render 
        [width, height, sortDocumentsBy, colorCertaintyBy, data]); // Conditions

    return(
        <div className={styles.container} ref={containerRef}>
            <svg ref={svgRef}>
                <g className="entityLegend"></g>
                <g className="certaintyLegend"></g>
                <g className="entities">
                    <text className="title"></text>
                    <g className="docLabels"></g>
                    <g className="entityCells"></g>
                </g>
                <g className="certainty">
                    <text className="title"></text>
                    <g className="docLabels"></g>
                    <g className="entityCells"></g>
                </g>
            </svg>
        </div>
    )
}

PixelCorpus.prototype.description = 'Display certainty, category, authorship and other information over a word-wise document representation.';

PixelCorpus.prototype.getConfigOptions = getConfig;

export default PixelCorpus;