import React from 'react';
import {useEffect, useState} from 'react';
import {DataService} from '../../../data';

let status = {fetching: 0, filtering: 0};

function useStatus(){
	const [value, setValue] = useState(0);

	useEffect(()=>{
		DataService.subscribeToStatus((args)=>{
			switch(args.action){
				case 'fetched':
					status.fetching --;
					break;
				case 'fetching':
					status.fetching ++;
					break;
				case 'filtered':
					status.filtering --;
					break;
				case 'filtering':
					status.filtering ++;
					break;
			}
			setValue(Object.assign({},status));
		})
	}, []);
}

export default function Status(){
	useStatus();

	const msg = status.fetching + status.filtering == 0
		? 'Idle'
		: ((status.fetching==0?'':'Fetching data') + (status.filtering==0?'':'Filtering data'));

	return(
		<button
			disabled
            type="button" 
            className="btn btn-secondary h-75 mr-3">
            {msg}
        </button>
	);
}