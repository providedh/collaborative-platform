import React from 'react';
import styles from './style.module.css';

export default function ColorControl({name, value='#fff', onValueChange, params}) {
    const handleChange = e=>onValueChange(e.target.value);

    return(
        <div className={styles.colorControl}>
            <div className={"form-group "+styles.formGroupOverride}>
                <label htmlFor={'input-'+name}>{name}</label>
                <input 
                    value={value} 
                    onChange={handleChange} 
                    type="color" 
                    className="form-control" 
                    id={'input-'+name} />
            </div>
        </div>
    )
}
