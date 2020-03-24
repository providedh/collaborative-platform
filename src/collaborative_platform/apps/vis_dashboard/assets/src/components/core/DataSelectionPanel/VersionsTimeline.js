import React from 'react';
import { useState, useEffect } from 'react';
import styles from './style.module.css';

export default function ProjectVersionTimeline({selected, versions=[], onChange}) {
    //versions.map(v=>console.log(v.date, selected.date, v.date <= selected.date))

    const timestamp = (v,i)=>(
        <div key={i} 
                className={`d-flex ${styles.timestamp} ${+v.version <= +selected.version?styles.selected:""}`}
                onClick={()=>onChange(v)}>
            <span className={`border ${styles.icon}`}/>
            <div className="pl-3">
                <h6 className="pl-0">{v.date.toUTCString()}</h6>
                {v.files.length} Commits in this project version by {[...new Set(v.files.map(x=>x.author))].join(', ')}
            </div>
        </div>
    )

    return(
        <div className={styles.timeline}>
            <span className={styles.timeBar}>
            <span>Present day</span>
            <span/>
            <span style={{height: (100*versions.length)+'px'}}/>
            <span/>
            <span>Project creation</span>
            </span>
            {versions.map((v,i)=>timestamp(v,i))}
        </div>
    )
}
