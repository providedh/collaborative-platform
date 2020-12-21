import React from 'react';
import {useEffect, useState} from 'react';


function useHistory(projectId){
	const [history, setHistoryCount] = useState(['loading project versions . . .']);

	useEffect(() => {
		fetch(`/overview/project/${projectId}/api/`)
			.then(response => response.json())
			.then(({versions}) => setHistoryCount(versions));
	}, []);

	return history;
}

function HistoryEntries({history}){
	const entries = history.map(d =>
		<li key={d.version}>
			Project version v{d.version} <span className="text-muted">created by: {d.author}</span>
		</li>)

	return <ul className="list-unstyled bg-light text-dark border p-3">
		{entries}
	</ul>
}

export default function App({appConfig}){
	const history = useHistory(appConfig.project_id);
	const entityTypeCount = Object.keys(appConfig.preferences.entities).length;
	console.log(appConfig)

	return(
		<div>
			<h3>Entity types count: {entityTypeCount}</h3>
			<h3>Project versions count: {history.length}</h3>
			<HistoryEntries history={history}/>
		</div>
	);
}