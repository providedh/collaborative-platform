import React from 'react';
import styles from './style.module.css';

import SidePanel from '../../ui/SidePanel';
import AddViewPanel from '../AddViewPanel';
import DataSelectionPanel from '../DataSelectionPanel';

export default function DashboardControlPanel({authors, versions, currentVersion, addView, setAuthors, setVersion, display}) {
    return(
        <SidePanel title="Dashboard Controls" labels={["Add View", "Data"]} display={display}>
            <div className={styles.panelArea}>
                <AddViewPanel addView={addView} />
            </div>
            <div className={styles.panelArea}>
                <DataSelectionPanel 
                    authors={authors} 
                    versions={versions}
                    currentVersion={currentVersion} 
                    setAuthors={setAuthors} 
                    setVersion={setVersion}
                />
            </div>
        </SidePanel>
    )
}
