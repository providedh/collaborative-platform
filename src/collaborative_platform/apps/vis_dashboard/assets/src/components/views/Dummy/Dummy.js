import React from 'react';
import styles from './style.module.css';
import getConfig from './config';

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

Dummy.prototype.getConfigOptions = getConfig;

export default Dummy;
