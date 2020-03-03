import React from 'react';
import styles from './style.module.css';

import SidePanel from '../../ui/SidePanel';
import AddViewPanel from '../AddViewPanel';
import DataSelectionPanel from '../DataSelectionPanel';

export default function DashboardControlPanel({authors, version, addView, setAuthors, setVersion, display}) {
    return(
        <SidePanel title="Dashboard Controls" labels={["Add View", "Theme", "Data"]} display={display}>
            <div className={styles.panelArea}>
                <AddViewPanel addView={addView} />
            </div>
            <div className={styles.panelArea}>
                <span>theme</span>
            </div>
            <div className={styles.panelArea}>
                <DataSelectionPanel 
                    authors={authors} 
                    version={version} 
                    setAuthors={setAuthors} 
                    setVersion={setVersion}
                />
            </div>
        </SidePanel>
    )
}
