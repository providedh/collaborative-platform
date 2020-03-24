import React from 'react';
import { useState, useEffect } from 'react';
import styles from './style.module.css';

import VersionsTimeline from './VersionsTimeline';
import Form from '../../ui/Form';

//{
//    resolve([
//        {
//            id: 'asd',
//            date: new Date(2019, 4, 12, 13),
//            commit_counter: 27,
//        },
//        {
//            id: 'asda',
//            date: new Date(2019, 2, 7, 14),
//            commit_counter: 19,
//        },
//        {
//            id: 'asdi',
//            date: new Date(2019, 1, 2, 17),
//            commit_counter: 16,
//        },
//        {
//            id: 'asdo',
//            date: new Date(2019, 1, 2, 11),
//            commit_counter: 10,
//        },
//    ])
//}

export default function DataSelectionPanel({versions, currentVersion, authors=[], setVersion, setAuthors}) {
    const collaborators = ['Me', 'Alex', 'Alicia', 'Juan'];
    const handleAuthorChange = conf=>setAuthors(conf[0].value);

    return(
        <div className={styles.dataSelectionPanel}>
            <h5>Authorships</h5>
            <h6>Only consider work of</h6>
            <Form options={[{
                name: 'Only consider work from', 
                type: 'compactMultipleSelection', 
                value: authors, 
                params: {options: collaborators}},]} 
                onUpdate={handleAuthorChange}/>
            <h5 className="mt-3">Data Versioning</h5>
            <h6>Use a specific version of the project</h6>
            <VersionsTimeline versions={versions} selected={currentVersion} onChange={setVersion} />
        </div>
    )
}
