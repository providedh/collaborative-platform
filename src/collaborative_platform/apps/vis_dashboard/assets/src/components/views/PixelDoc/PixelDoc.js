import React from 'react';
import styles from './style.module.css';
import css from './style.css';
import data from './data';

function PixelDoc({documentId, dimension}) {
    const dimension2index = {
        'entityType': 0,
        'certaintyType': 1,
        'certaintyLevel': 2
    }

    const key2label = {
        'entityType-p': 'Person',
        'entityType-t': 'Time',
        'entityType-d': 'Date',
        'entityType-l': 'Location',
        'entityType-e': 'Event',
        'entityType-r': 'Organization',
        'entityType-o': 'Object',
        'entityType-n': 'Not an entity',
        'certaintyType-i': 'Ignorance',
        'certaintyType-c': 'Credibility',
        'certaintyType-m': 'Imprecision',
        'certaintyType-n': 'None',
        'certaintyType-s': 'Incompleteness',
        'certaintyLevel-1': 'Very low',
        'certaintyLevel-2': 'Low',
        'certaintyLevel-3': 'Medium',
        'certaintyLevel-4': 'High',
        'certaintyLevel-5': 'Very high',
        'certaintyLevel-0': 'Unknown',
        'certaintyLevel-n': 'Not registered',
    }

    function renderLine(line, index){
        const cells = line.map((c, i) => (
            <span key={i} 
                title={key2label[dimension+'-'+c[dimension2index[dimension]]]}
                className={`${styles.token} ${styles[dimension+'-'+c[dimension2index[dimension]]]}`} />
        ))
        return <div key={index} className={styles.line}>{cells}</div>
    }

    return(
        <div className={styles.pixelDoc}>
            {data[documentId].map((line,i) => renderLine(line, i))}
        </div>
    )
}

PixelDoc.prototype.configOptions = [
    {name: 'documentId', type: 'selection', value: '#1', params: {options: ['#1', '#2', '#3']}},
    {name: 'dimension', type: 'selection', value: 'entityType', params: {options: ['entityType', 'certaintyType', 'certaintyLevel']}},
];

export default PixelDoc;
