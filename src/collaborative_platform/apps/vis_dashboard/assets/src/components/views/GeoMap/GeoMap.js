import React from 'react';
import styles from './style.module.css';
import css from './style.css';
import data from './data';
import * as d3 from 'd3';

function useProjectionUpdates(){}
function useDataUpdates(){}
function useScaleUpdates(){}
function useVisUpdates(){}
function useSizeUpdates(){}

function GeoMap({documentId, dimension}) {
    console.log(d3)
    return(
        <div className={styles.geoMap}>
            
        </div>
    )
}

GeoMap.prototype.description = 'Display entities, documents and other data in a geographical projection.';

GeoMap.prototype.configOptions = [
    {name: 'documentId', type: 'selection', value: '#1', params: {options: ['#1', '#2', '#3']}},
    {name: 'dimension', type: 'selection', value: 'entityType', params: {options: ['entityType', 'certaintyType', 'certaintyLevel']}},
];

export default GeoMap;
