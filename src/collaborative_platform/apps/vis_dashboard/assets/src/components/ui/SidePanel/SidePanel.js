import React from 'react';
import styles from './style.module.css';

import TabContainer from '../TabContainer';

export default function SidePanel({title, labels, onClose=null, display, children}) {
    return(
        <div className={styles.sidePanel + (display===true?'':' d-none')}>
            <div className={styles.header}>
                {title}
                {onClose == null ? '' : 
                    <button type="button" 
                            className="close" 
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
