import React from 'react';
import styles from './style.module.css';

import SidePanel from '../../ui/SidePanel';
import AddViewPanel from '../AddViewPanel';

export default function DashboardControlPanel({addView, display}) {
    return(
        <SidePanel title="Dashboard Controls" labels={["Add View", "Theme", "Filters"]} display={display}>
            <div className={styles.panelArea}>
                <AddViewPanel addView={addView} />
            </div>
            <div className={styles.panelArea}>
                <span>theme</span>
            </div>
            <div className={styles.panelArea}>
                <span>filters</span>
            </div>
        </SidePanel>
    )
}
