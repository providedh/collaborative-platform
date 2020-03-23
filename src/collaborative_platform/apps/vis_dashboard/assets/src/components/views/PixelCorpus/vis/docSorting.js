
function mostSelfContributedFirst(entities, annotations){
	const docs = [...(new Set(entities.map(e=>e.file_name))).values()];
	const sorted = docs.map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function leastSelfContributedFirst(entities, annotations){
	const docs = [...(new Set(entities.map(e=>e.file_name))).values()];
	const sorted = docs.map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function lastEditedFirst(entities, annotations){
	const docs = [...(new Set(entities.map(e=>e.file_name))).values()];
	const sorted = docs.map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function lastEditedLast(entities, annotations){
	const docs = [...(new Set(entities.map(e=>e.file_name))).values()];
	const sorted = docs.map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function higherEntityCountFirst(entities, annotations){
	const docs = {};
	for(let e of entities){
		if(!docs.hasOwnProperty(e.file_name))
			docs[e.file_name] = 0;
		docs[e.file_name] ++;
	}

	const sorted = Object.keys(docs).sort((x, y)=>docs[y] - docs[x]).map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function higherEntityCountLast(entities, annotations){
	const docs = {};
	for(let e of entities){
		if(!docs.hasOwnProperty(e.file_name))
			docs[e.file_name] = 0;
		docs[e.file_name] ++;
	}

	const sorted = Object.keys(docs).sort((x, y)=>docs[x] - docs[y]).map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

export default {
	mostSelfContributedFirst,
	leastSelfContributedFirst,
	lastEditedFirst,
	lastEditedLast,
	higherEntityCountFirst,
	higherEntityCountLast,
}