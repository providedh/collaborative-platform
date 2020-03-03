import React from 'react';
import styles from './style.module.css';
import css from './style.css';

export default function VisFrame({index, focused, onViewFocus, onViewClose, children}) {
    return(
        <div className={`border ${styles.frame} ${focused?'focused border-primary':''}`}>
            <div className={styles.topbar}>
                <button onClick={()=>onViewClose(index)} type="button" className="close" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
                <button onClick={()=>onViewFocus(index)} type="button" className="close" aria-label="Close">
                  <span aria-hidden="true">&#9881;</span>
                </button>
            </div>
            <div className={styles.container}>
                {children}
            </div>
        </div>
    )
}
