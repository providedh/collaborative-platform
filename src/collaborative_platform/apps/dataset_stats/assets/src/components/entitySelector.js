import React from 'react';
import {useState, useEffect} from 'react';

import LoadingComponent from './loading';

const entityPreset = 
	['person', 'event', 'org', 'object', 'place', 'date', 'time'];

function useEntities(stats){
	const [entities, setEntities] = useState([]);

	useEffect(()=>{
		const newEntities = stats.map(e=>[e.name, e.long_name, entityPreset.includes(e.name)]);
		setEntities(newEntities);
	},[stats]);

	const toggleEntity = (e)=>{
		const newEntities = entities.map(([name, long_name, checked])=>[name, long_name, name!=e?checked:!checked]);
		setEntities(newEntities);
	}

	return [entities, toggleEntity];
}

function useDisplayChecks(entities){
	useEffect(()=>{
		for(let [entity, long_name, shouldShow] of entities){
			const node = document.getElementById(long_name);

			if(shouldShow) node.classList.remove('d-none');
			else node.classList.add('d-none');
		}
	},[entities]);
}

export default function({stats}){
	const [entities, toggleEntity] = useEntities(stats);
	useDisplayChecks(entities);

	let content = '';

	if(entities.length == 0){
		content = <LoadingComponent />;
	}else{

		content = entities.map(([entity, long_name, checked])=>(
			<div key={long_name} className="form-check form-check-inline">
				<input className="form-check-input" 
					type="checkbox" 
					checked={checked}
					id={entity + 'check'} 
					onChange={()=>toggleEntity(entity)}/>
				<label className="form-check-label" htmlFor={entity + 'check'}>
			    	{entity[0].toUpperCase() + entity.slice(1).toLowerCase()}
			  	</label>
			</div>));
	}

	return(
		<div className="box">
	        <div className="box__header">
	          	<h3 className="box__text--title">Available entities</h3>
	        </div>
	        <div id="entitySelector" className="box__content">
	          	{content}
	        </div>
      	</div>
	);
}