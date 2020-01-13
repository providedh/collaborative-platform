import React from 'react';
import styles from './style.module.css';

import SidePanel from '../../ui/SidePanel';
import Views from '../../views';
import Form from '../../ui/Form';

export default function ViewDetailsPanel({view, display, updateView, close}) {

    const options = Views[view.type].prototype.configOptions;
    for(let option of options)
        option.value = view.config[option.name];

    function handleUpdateView(formValues){
        const newConfig = {};

        for(let formValue of formValues)
            newConfig[formValue.name] = formValue.value;
        updateView(newConfig)
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
