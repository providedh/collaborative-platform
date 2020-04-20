import React, {useState, useEffect} from 'react';
import * as d3Array from 'd3-array';

export default function useData(dataClient, option){
	const [data, setData] = useState(null);

	if(!Object.hasOwnProperty.call(dataOptions, option))
		return
	
	useEffect(()=>{
		dataOptions[option](dataClient, setData);
		return dataClient.clearFiltersAndSubscriptions;
	}, [option]);

	return data;
}

const dataOptions = {
	entitiesPerDoc,
	entitiesPerType,
	commonEntities,
	annotationsPerDoc,
	annotationsPerCategory,
	annotationsPerAuthor,
	commonAttributeValues,
	annotationAttributes,
}

function entitiesPerDoc(dataClient, setData){
	dataClient.subscribe('entity', ({all, filtered})=>{
		setData({
			dimension: 'file_id',
			filterDimension: 'fileId',
			all: d3Array.group(all, x=>x.file_id),
			filtered: d3Array.group(filtered, x=>x.file_id)
		});
	});
}

function entitiesPerType(dataClient, setData){
	dataClient.subscribe('entity', ({all, filtered})=>{
		setData({
			dimension: 'type',
			filterDimension: 'entityType',
			all: d3Array.group(all, x=>x.type),
			filtered: d3Array.group(filtered, x=>x.type)
		});
	});	
}

function commonEntities(dataClient, setData){
	return 0;
	dataClient.subscribe('certainty', ({all, filtered})=>{
		alert('The entity type of the annotated piece is not yet exposed');
		//setData({
		//	dimension: 'type',
		//	filterDimension: 'fileId',
		//	all: d3Array.group(all, x=>x.file),
		//	filtered: d3Array.group(filtered, x=>x.file)
		//});
	});
}

function annotationsPerDoc(dataClient, setData){
	dataClient.subscribe('certainty', ({all, filtered})=>{
		setData({
			dimension: 'file id',
			filterDimension: 'fileId',
			all: d3Array.group(all, x=>x.file),
			filtered: d3Array.group(filtered, x=>x.file)
		});
	});
}

function annotationsPerCategory(dataClient, setData){
	dataClient.subscribe('certainty', ({all, filtered})=>{
		setData({
			dimension: 'category',
			filterDimension: 'certaintyCategory',
			all: d3Array.group(all, x=>x.category.sort().join()),
			filtered: d3Array.group(filtered, x=>x.category.sort().join())
		});
	});
}

function annotationsPerAuthor(dataClient, setData){
	dataClient.subscribe('certainty', ({all, filtered})=>{
		setData({
			dimension: 'author',
			filterDimension: 'author',
			all: d3Array.group(all, x=>x.resp),
			filtered: d3Array.group(filtered, x=>x.resp)
		});
	});
}

function commonAttributeValues(dataClient, setData){
	dataClient.subscribe('entity', ({all, filtered})=>{

	});
}

function annotationAttributes(dataClient, setData){
	dataClient.subscribe('certainty', ({all, filtered})=>{
		console.log(all, filtered)
		setData({
			dimension: 'attribute',
			filterDimension: 'certaintyMatch',
			all: d3Array.group(all, x=>x.match),
			filtered: d3Array.group(filtered, x=>x.match)
		});
	});
}