import React from 'react';
import {useEffect, useState} from 'react';

import EntitySelector from './entitySelector';
import ProjectStats from './projectStats';
import Timeline from '../helpers/timeline';
import Ajax from '../helpers/ajax';

const ajax = Ajax();

function useTimeline(setVersion){
	useEffect(()=>{
		Timeline()
			.onVersionSelect(p=>setVersion(p.version))
			.load()
			.then(versions=>setVersion(versions[versions.length-1].version));
		},[]);
}

function useProjectVersion(){
	const [projectVersion, setProjectVersion] = useState('loading versions . . .');
	const [stats, setStats] = useState([]);

	function setVersion(v){
		setProjectVersion(`fetching data . . .`);
		setStats([]);
		ajax.getStats(window.project_id, v).then(res=>{
			if(res.success === true){
				setProjectVersion(`v.${v}`);
				setStats(res.content.entities);
			}
		});
	}

	return [projectVersion, stats, setVersion];
}

function useProjectVersionLabel(projectVersion){
	useEffect(()=>{
			document.getElementById('project-version-label').innerText = projectVersion;
		}, 
		[projectVersion]);
}

export default function App(){
	const [projectVersion, stats, setVersion] = useProjectVersion();
	useTimeline(setVersion);
	useProjectVersionLabel(projectVersion)

	return(
		<div>
			<EntitySelector currentSelection={null}/>
			<ProjectStats stats={stats}/>
		</div>
	);
}