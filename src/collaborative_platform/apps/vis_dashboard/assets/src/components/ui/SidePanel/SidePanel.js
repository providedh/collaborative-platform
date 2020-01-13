import React from 'react';
import styles from './style.module.css';

import TabContainer from '../TabContainer';

export default function SidePanel({title, labels, onClose=null, display, children}) {
    return(
        <div className={styles.sidePanel + (display===true?'':' d-none')}>
            <div className={styles.header}>
                <h5>{title}</h5>
                {onClose == null ? '' : 
                    <button type="button" 
                            className="close mr-4 mt-4" 
                            aria-label="Close"
                            onClick={onClose}>
                        <span aria-hidden="true">&times;</span>
                    </button>}
            </div>
            <hr className="hr"/>

            <TabContainer labels={labels}>
                {children}
            </TabContainer>
        </div>
    )
}
