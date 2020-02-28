import React from 'react';

import EntitySelector from './entitySelector';
import ProjectStats from './projectStats';
import Timeline from '../helpers/timeline';


const timeline = Timeline()
	.onVersionSelect(p=>alert('selected version '+p.version))
	.load();

export default function App(){
	
	return(
		<div>
			<EntitySelector currentSelection={null}/>
			<ProjectStats stats={[
				{
					name: 'place',
					count: 12,
					coverage: 30,
					location: 'header',
					distinct_doc_occurrences: 3,
					document_count: 10,
					attributes: []
				},
				{
					name: 'person',
					count: 22,
					coverage: 80,
					location: 'body',
					distinct_doc_occurrences: 8,
					document_count: 10,
					attributes: [
						{
							name: 'age',
							distinct_values: 3,
							trend_percentage: 80,
							trend_value: 35,
							coverage: 30
						}
					]
				}
				]}/>
		</div>
	);
}