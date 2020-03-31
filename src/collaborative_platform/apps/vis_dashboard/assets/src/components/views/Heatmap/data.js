import {useEffect, useState} from "react";

export default function useData(dataClient, source, axis1name, axis2name){
	const [data, setData] = useState(null);

	useEffect(()=>{
        const {preprocessing, getEntriesAndAxis} = 
        	source=='entity'?entityProcessing():certaintyProcessing();

        dataClient.unsubscribe('entity');
        dataClient.unsubscribe('certainty');
        dataClient.subscribe(source, data=>{
        	if(data == null || data.all.length == 0 || data.filtered.length == 0)
                return 0;

            const preprocessed = preprocessing(data),
            	[entries, axis1, axis2] = getEntriesAndAxis(preprocessed, axis1name, axis2name),
            	[concurrenceMatrix, maxOccurrences] = getConcurrenceMatrix(entries, axis1, axis2),
            	processed = {concurrenceMatrix, maxOccurrences, axis1, axis2};
        	
        	setData(processed);
        });

	}, [source, axis1name, axis2name])

	return data;
}

function getAttribute(x, attr){
	let attrName = attr;

	if(attr == 'documentName')
		attrName = 'file_name';
	else if(attr == 'text')
		attrName = 'name';

	return ''+x[attrName];
}

function entityProcessing(){
	function preprocessing(data){
		return data.filtered;
	}

	function getEntriesAndAxis(data, axis1name, axis2name){
		const axis1 = {name: axis1name, values: new Set()},
			axis2 = {name: axis2name, values: new Set()},
			entries = data.map(x=>{
				axis1.values.add(getAttribute(x, axis1name));
				axis2.values.add(getAttribute(x, axis2name));
				
				return{ 
					name:x.name, 
					id:x.id, 
					axis1:getAttribute(x, axis1name), 
					axis2:getAttribute(x, axis2name)
				};
			});

		axis1.values = [...axis1.values.values()];
		axis2.values = [...axis2.values.values()];

		return [entries, axis1, axis2];
	}

	return {preprocessing, getEntriesAndAxis}
}

function certaintyProcessing(){
	function preprocessing(data){
		return data.all;
	}

	function getEntriesAndAxis(data, axis1name, axis2name){
		const axis1 = {name: axis1name, values: new Set()},
			axis2 = {name: axis2name, values: new Set()},
			entries = data.map(x=>({name:'', id:'', axis1:'', axis2:''}));


		return [entries, [...axis1.values()], [...axis2.values()]];
	}

	return {preprocessing, getEntriesAndAxis}
}


function getConcurrenceMatrix(entries, axis1, axis2){
	let maxOccurrences = 0;
	const concurrenceMatrix = Object.fromEntries(axis1.values.map(x=>[x,null]));
		axis1.values.forEach(x=>concurrenceMatrix[x] = Object.fromEntries(axis2.values.map(y=>[y, []])));
	entries.forEach(x=>{
		concurrenceMatrix[x.axis1][x.axis2].push(x);
		if(concurrenceMatrix[x.axis1][x.axis2].length > maxOccurrences)
			maxOccurrences = concurrenceMatrix[x.axis1][x.axis2].length;
	});

	return [concurrenceMatrix, maxOccurrences];
}