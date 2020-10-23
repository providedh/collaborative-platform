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
	const [docCount, setDocCount] = useState(0)

	function setVersion(v){
		setProjectVersion(`fetching data . . .`);
		setStats([]);
		ajax.getStats(window.project_id, v).then(res=>{
			if(res.success === true){
				setProjectVersion(`v.${v}`);
				setStats(res.content.entities);
				setDocCount(res.content.document_count)
			}
		});
	}

	return [projectVersion, stats, docCount, setVersion];
}

function useProjectVersionLabel(projectVersion){
	useEffect(()=>{
			document.getElementById('project-version-label').innerText = projectVersion;
		}, 
		[projectVersion]);
}

export default function App(){
	const [projectVersion, stats, docCount, setVersion] = useProjectVersion();
	useTimeline(setVersion);
	useProjectVersionLabel(projectVersion)

	return(
		<div>
			<EntitySelector stats={stats}/>
			<ProjectStats stats={stats} docCount={docCount}/>
		</div>
	);
}