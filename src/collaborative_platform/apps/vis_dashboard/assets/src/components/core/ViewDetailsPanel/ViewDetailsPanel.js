import React from 'react';
import styles from './style.module.css';

import SidePanel from '../../ui/SidePanel';
import Views from '../../views';
import Form from '../../ui/Form';

export default function ViewDetailsPanel({view, display, updateView, close}) {
    const form = Object.entries(view.config).map(([key, value])=>{
        const entry = {};
        entry.name = key;
        entry.value = value;
        return entry;
    });
    const options = Views[view.type].prototype.getConfigOptions(form);
    
    function handleUpdateView(formValues){
        const newConfig = {};
        formValues.forEach(x=>newConfig[x.name]=x.value);
        //console.log(view.config, view.type, newConfig, formValues)
        updateView(newConfig);
    }

    return(
        <SidePanel title="View Details" labels={["View Params", "Style"]} display={display} onClose={close}>
            <div className={styles.panelArea}>
                {view!=null && (
                    <div>
                    <Form options={options} onUpdate={handleUpdateView} />
                    </div>
                )
                }
            </div>
            <div className={styles.panelArea}>
                <span>styling</span>
            </div>
        </SidePanel>
    )
}
