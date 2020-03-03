import React from 'react';
import styles from './style.module.css';

export default function MultipleSelectionControl({name, value=[], onValueChange, params={options: []}}) {
    const handleChange = e=>{
        const option = e.target.value,
            newValue = value.includes(option)?value.filter(x=>x!=option):[...value, option]
        onValueChange(newValue)
    };

    return(
        <div className={styles.multipleSelectionControl}>
            <div className={"form-group "+styles.formGroupOverride}>
                <label>{name}</label>
                <div className={styles.options}>
                    {params.options.map((o, i) => (
                        <div key={i} className={"form-group form-check "+styles.formGroupOverride}>
                            <input 
                                id={'input-'+name+o}
                                type="checkbox" 
                                className="form-check-input" 
                                value={o}
                                checked={value.includes(o)} 
                                onChange={handleChange}/>
                            <label className="form-check-label" htmlFor={'input-'+name+o}>{o}</label>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
