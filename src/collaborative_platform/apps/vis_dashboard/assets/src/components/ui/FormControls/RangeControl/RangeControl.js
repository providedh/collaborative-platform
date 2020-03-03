import React from 'react';
import styles from './style.module.css';

export default function RangeControl({name, value=0, onValueChange, params={range: [0, 100]}}) {
    const handleChange = e=>onValueChange(e.target.value);

    return(
        <div className={styles.rangeControl}>
            <div className={"form-group "+styles.formGroupOverride}>
                <label htmlFor={'input-'+name}>{name}</label>
                <input 
                    type="range" 
                    value={value} 
                    onChange={handleChange} 
                    min={params.range[0]}
                    max={params.range[1]}
                    className="form-control-range" 
                    id={'input-'+name} />
                <span>{value}</span>
            </div>
        </div>
    )
}
