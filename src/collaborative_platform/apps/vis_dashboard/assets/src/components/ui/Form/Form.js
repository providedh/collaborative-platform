import React from 'react';
import styles from './style.module.css';

import FormControls from '../FormControls';

export default function Form({options ,onUpdate}) {
    const name2index = {};
    options.forEach((o,i) => name2index[o.name]=i);

    function handleChange(name, value) {
        const newOptions = Array.from(options);
        newOptions[name2index[name]].value = value;
        onUpdate(newOptions);
    }

    function renderInputs(){
        return options.map(o => (
            <div className={'row ' + styles.rowOverride} key={o.name}>
                {React.createElement(FormControls[o.type], {
                    key: o.name,
                    name: o.name,
                    value: o.value,
                    onValueChange: value=>handleChange(o.name, value),
                    params: o.params
                })}
            </div>
        ))
    }

    return(
        <div className={styles.form}>
            {renderInputs()}
        </div>
    )
}
