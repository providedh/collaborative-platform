import React from 'react';
import styles from './style.module.css';

import SelectionControl from '../SelectionControl';

export default function DocumentControl({name, value='', onValueChange, params}) {
    params = {options: ['#1', '#2', '#11']}
    return(
        <div className={styles.documentControl}>
            <SelectionControl {...{name, value, onValueChange, params}} />
        </div>
    )
}
