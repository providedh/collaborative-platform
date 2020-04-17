import React from 'react';
import styles from './style.module.css';

import SidePanel from '../../ui/SidePanel';
import Views from '../../views';
import Form from '../../ui/Form';
import {WithAppContext} from 'app_context';

export default (props)=>(
    <WithAppContext>
        <ViewDetailsPanel {...props}/>
    </WithAppContext>
);

function ViewDetailsPanel({view, display, updateView, close, context}) {
    const form = Object.entries(view.config).map(([key, value])=>{
        const entry = {};
        entry.name = key;
        entry.value = value;
        return entry;
    });
    const options = Views[view.type].prototype.getConfigOptions(form, context);
    
    function handleUpdateView(formValues){
        // This creates a new configuration from the old one with the replaced new
        // value; which does not ensure that is a valid configuration for the view.
        // const newConfig = Object.fromEntries(formValues.map(x=>[x.name, x.value]));

        // The getConfigOptions method already returns a correct set of options and 
        // defaults. The updated view configuration is ensured to be valid. 
        const formValuesValidated = Views[view.type].prototype.getConfigOptions(formValues, context);
        const newConfig = Object.fromEntries(
            formValuesValidated.map(x=>[x.name, x.value])
        );
        
        updateView(newConfig);
    }

    return(
        <SidePanel title="View Details" labels={["Parameters"]} display={display} onClose={close}>
            {[<div key="details" className={styles.panelArea}>
                {view!=null && (
                    <div>
                    <Form options={options} onUpdate={handleUpdateView} />
                    </div>
                )
                }
            </div>]}
        </SidePanel>
    )
}
