import React from 'react';
import styles from './style.module.css';

export default function NumberControl({name, value, onValueChange, params}) {
    const handleChange = e=>onValueChange(e.target.value);

    return(
        <div className={styles.numberControl}>
            <div className={"form-group "+styles.formGroupOverride}>
                <label htmlFor={'input-'+name}>{name}</label>
                <input 
                    value={value} 
                    onChange={handleChange} 
                    type="number" 
                    className="form-control" 
                    id={'input-'+name} />
            </div>
        </div>
    )
}
