
function mostSelfContributedFirst(data, fileAccessor){
	const docs = [...(new Set(data.map(e=>fileAccessor(e)))).values()];
	const sorted = docs.map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function leastSelfContributedFirst(data, fileAccessor){
	const docs = [...(new Set(data.map(e=>fileAccessor(e)))).values()];
	const sorted = docs.map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function lastEditedFirst(data, fileAccessor){
	const docs = [...(new Set(data.map(e=>fileAccessor(e)))).values()];
	const sorted = docs.map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function lastEditedLast(data, fileAccessor){
	const docs = [...(new Set(data.map(e=>fileAccessor(e)))).values()];
	const sorted = docs.map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function higherEntityCountFirst(data, fileAccessor){
	const docs = {};
	for(let e of data){
		if(!docs.hasOwnProperty(fileAccessor(e)))
			docs[fileAccessor(e)] = 0;
		docs[fileAccessor(e)] ++;
	}

	const sorted = Object.keys(docs).sort((x, y)=>docs[y] - docs[x]).map((x,i)=>[x,i]);

	return Object.fromEntries(sorted);
}

function higherEntityCountLast(data, fileAccessor){
	const docs = {};
	for(let e of data){
		if(!docs.hasOwnProperty(fileAccessor(e)))
			docs[fileAccessor(e)] = 0;
		docs[fileAccessor(e)] ++;
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