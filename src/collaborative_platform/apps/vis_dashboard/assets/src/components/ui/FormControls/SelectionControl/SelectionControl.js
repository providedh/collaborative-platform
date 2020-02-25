import React from 'react';
import styles from './style.module.css';

export default function SelectionControl({name, value='', onValueChange, params={options: []}}) {
    const handleChange = e=>onValueChange(e.target.value);

    function createLabel(name){
        const separated = name.replace(/[A-Z]/g, x=>' '+x),
            capitalized = separated[0].toUpperCase() + separated.slice(1).toLowerCase();
        return capitalized;
    }

    return(
        <div className={styles.selectionControl}>
            <div className={"form-group "+styles.formGroupOverride}>
                <label htmlFor={'input-'+name}>{createLabel(name)}</label>
                <select className="form-control" value={value} onChange={handleChange}>
                    {params.options.map((o, i) => <option value={o} key={i}>{o}</option>)}
                </select>
            </div>
        </div>
    )
}
