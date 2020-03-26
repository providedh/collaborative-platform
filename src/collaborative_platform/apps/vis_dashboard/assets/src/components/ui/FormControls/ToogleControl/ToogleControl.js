import React from 'react';
import styles from './style.module.css';

export default function ToogleControl({name, value=true, onValueChange, params}) {
    const handleChange = e=>onValueChange(e.target.checked);

    function createLabel(name){
        const separated = name.replace(/[A-Z]/g, x=>' '+x),
            capitalized = separated[0].toUpperCase() + separated.slice(1).toLowerCase();
        return capitalized;
    }

    return(
        <div className={styles.toogleControl}>
            <div className={"form-group form-check "+styles.formGroupOverride}>
                <input 
                    id={'input-'+name}
                    type="checkbox" 
                    className="form-check-input" 
                    value={value}
                    checked={value}
                    onChange={handleChange}/>
                <label className="form-check-label" htmlFor={'input-'+name}>{createLabel(name)}</label>
            </div>
        </div>
    )
}
