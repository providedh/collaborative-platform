import React from 'react';
import styles from './style.module.css';

export default function multipleSelectionControl({name, value='', onValueChange, params={options: []}}) {
    const handleChange = e=>onValueChange(e.target.value);

    return(
        <div className={styles.multipleSelectionControl}>
            <div className={"form-group "+styles.formGroupOverride}>
                <label htmlFor={'input-'+name}>{name}</label>
                <select multiple value={value} onChange={handleChange}>
                    {params.options.map((o, i) => <option value={o} key={i}>{o}</option>)}
                </select>
            </div>
        </div>
    )
}
