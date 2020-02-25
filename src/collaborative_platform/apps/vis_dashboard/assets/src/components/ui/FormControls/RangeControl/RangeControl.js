import React from 'react';
import styles from './style.module.css';

export default function RangeControl({name, value=0, onValueChange, params={range: [0, 100]}}) {
    const handleChange = e=>onValueChange(e.target.value);

    function createLabel(name){
        const separated = name.replace(/[A-Z]/g, x=>' '+x),
            capitalized = separated[0].toUpperCase() + separated.slice(1).toLowerCase();
        return capitalized;
    }

    return(
        <div className={styles.rangeControl}>
            <div className={"form-group "+styles.formGroupOverride}>
                <label htmlFor={'input-'+name}>{createLabel(name)}</label>
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
