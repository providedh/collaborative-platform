import React from 'react';
import { useState, useEffect } from 'react';
import styles from './style.module.css';

import Views from '../../views';
import Form from '../../ui/Form';

function useViewType() {
    const [value, setValue] = useState(Object.keys(Views)[0])

    const onChange = e => setValue(e.target.value);

    return {value, onChange}
}

export default function AddViewPanel({addView}) {
    const viewType = useViewType();
    const [viewConfig, setViewConfig] = useState(Views[viewType.value].prototype.configOptions)

    useEffect(()=>setViewConfig(Views[viewType.value].prototype.configOptions), [viewType])

    function handleCreateView(){
        const newView = {type: viewType.value, config: {}};

        for(let config of viewConfig)
            newView.config[config.name] = config.value;
        addView(newView);
    }

    return(
        <div className={styles.addViewPanel}>
            <h1>{viewType.value}</h1>
            <select {...viewType}>
                {Object.keys(Views).map(o => <option key={o} value={o}>{o}</option>)}
            </select>
            <Form options={viewConfig} onUpdate={setViewConfig} />
            View creation panel <button onClick={handleCreateView}>Create</button>
        </div>
    )
}
