import React from 'react';
import styles from './style.module.css';

export default function ToogleControl({name, value=true, onValueChange, params}) {
    const handleChange = e=>onValueChange(e.target.checked);

    return(
        <div className={styles.toogleControl}>
            <div className={"form-group form-check "+styles.formGroupOverride}>
                <input 
                    id={'input-'+name}
                    type="checkbox" 
                    className="form-check-input" 
                    value={value} 
                    onChange={handleChange}/>
                <label className="form-check-label" htmlFor={'input-'+name}>{name}</label>
            </div>
        </div>
    )
}
