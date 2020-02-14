import React from 'react';
import styles from './style.module.css';

function Dummy({backgroundColor, documentId, childs, tickets, age, periodOfTime, name, power}) {
    return(
        <div className={styles.dummy}>
            <p>
            {backgroundColor}<br/>
            {documentId}<br/>
            {childs}<br/>
            {tickets}<br/>
            {age}<br/>
            {periodOfTime}<br/>
            {name}<br/>
            {power}<br/>
            </p>
        </div>
    )
}

Dummy.prototype.description = 'A dummy view for development and showcase of the platform functioning.';

Dummy.prototype.configOptions = [
    {name: 'backgroundColor', type: 'color', value: '#fff'},
    {name: 'documentId', type: 'documentId', value: '#1'},
    {name: 'dimension', type: 'selection', value: 'two', params: {options: ['content', 'entity', 'certainty']}},
    {name: 'tickets', type: 'multipleSelection', value: ['one','two'], params: {options: ['one', 'two', 'three']}},
    {name: 'gender', type: 'number', value: 21},
    {name: 'periodOfTime', type: 'range', value: 20, params:{ range: [0,100]}},
    {name: 'name', type: 'text', value: ''},
    {name: 'power', type: 'toogle', value: true},
];

export default Dummy;
