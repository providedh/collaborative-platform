import React from 'react';
import { useState, useEffect } from 'react';
import styles from './style.module.css';

import VersionsTimeline from './VersionsTimeline';
import Form from '../../ui/Form';

const fetchCollaborators = new Promise((resolve, error)=>{
    resolve(['Me', 'Alex', 'Alicia', 'Juan'])
})

function useCollaborators(){
    const [value, setValue] = useState([]);

    fetchCollaborators.then(collaborators=>setValue(collaborators));

    return value;
}

const fetchVersions = new Promise((resolve, error)=>{
    resolve([
        {
            id: 'asd',
            date: new Date(2019, 4, 12, 13),
            commit_counter: 27,
        },
        {
            id: 'asda',
            date: new Date(2019, 2, 7, 14),
            commit_counter: 19,
        },
        {
            id: 'asdi',
            date: new Date(2019, 1, 2, 17),
            commit_counter: 16,
        },
        {
            id: 'asdo',
            date: new Date(2019, 1, 2, 11),
            commit_counter: 10,
        },
    ])
})

function useVersions(){
    const [versions, setVersions] = useState([]);
    const [selected, setSelected] = useState(null);

    useEffect(()=>{fetchVersions.then(v=>{
        const versions = v.sort(x=>x.date);
        setSelected(versions[0]);
        setVersions(versions);
        })}, []);

    return [versions, selected, setSelected];
}

export default function DataSelectionPanel({version, authors=[], setVersion, setAuthors}) {
    const collaborators = useCollaborators();
    const [versions, selected, setSelected] = useVersions();

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
            <VersionsTimeline versions={versions} selected={selected} onChange={setSelected} />
        </div>
    )
}
