import React from 'react';

import LoadingComponent from './loading';
import EntityStats from './entityStats';

export default function({stats}){
	let content = ''
	if(stats == null || stats.length == 0){
		content = <LoadingComponent />;
	}else{
		content = stats.map((entity,i)=><EntityStats key={i} data={entity}/>);
	}

	return(
		<div className="box">
	        <div className="box__header">
	          	<h3 className="box__text--title">Entity and attribute coverage of the dataset</h3>
	        </div>
	        <div id="stats" className="box__content">
	          	{content}
	        </div>
      	</div>
	);
}