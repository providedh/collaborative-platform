import React from 'react';

import EntitySelector from './entitySelector';
import Timeline from '../helpers/timeline';


const timeline = Timeline()
	.onVersionSelect(p=>alert('selected version '+p.version))
	.load();

export default function App(){
	
	return(
		<div>
			<EntitySelector currentSelection={null}/>
		</div>
	);
}