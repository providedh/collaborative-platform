import React from 'react';
import PropTypes from 'prop-types';
import styles from './style.module.css';

export default function TabControl({labels, active, onChange}) {
    

    const createControls = () => labels.map((x,i)=>(
        <div key={x} id={x}  onClick={e=>onChange(x)}
             className={`col text-center ${styles.option} ${i==active?styles.selected:''}`}>
            <h5>{x}</h5>
        </div>)
    )

    return(
        <div className={styles.tabSelector}>
            <div className={"row " + styles.rowOverride}>
            	{createControls()}
            </div>
            <hr className={styles.hr}/>
        </div>
    )
}
