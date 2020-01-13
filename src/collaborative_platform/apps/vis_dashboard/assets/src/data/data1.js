/*
	Synthetic data for the design and implementation of a pixel-wise visualization
	Each three-character word represents the following:
	entity-category-certainty

	entity := [
		p // person
		t // time
		d // date
		l // location
		e // event
		r // organization
		o // object
		n // none
	]

	category := [
		i // ignorance
		c // credibility
		m // imprecision
		n // incompleteness
	]

	certainty := [
		0 // unknown
		1 // very low
		2 // low
		3 // medium
		4 // high
		5 // very high
	]
*/

const ENTITIES = [
		'p', // person
		't', // time
		'd', // date
		'l', // location
		'e', // event
		'n', // none
		'r', // organization
		'o', // object
	],
	CATEGORIES = [
		'i', // ignorance
		'c', // credibility
		'm', // imprecision
		'n', // none
		's', // incompleteness
	],
	CERTAINTIES = [
		0, // unknown
		1, // very low
		2, // low
		3, // medium
		4, // high
		5, // very high
		'n', // none
	]

export default function(minLines=20, maxLines=20, minWords=6, maxWords=12){
	const 
		lines = [], 
		lineCount = minLines + Math.trunc(Math.random() * (maxLines - minLines));

	for (let i = 0; i < lineCount; i++) {
		lines.push([]);
		
		const wordCount = minWords + Math.trunc(Math.random() * (maxWords - minWords));		
		for (let j = 0; j < wordCount; j++) {
			const 
				entity = ENTITIES[Math.trunc(Math.random() * (ENTITIES.length - 1))],
				category = CATEGORIES[Math.trunc(Math.random() * (CATEGORIES.length - 1))],
				cert = category=='n'?'n':CERTAINTIES[Math.trunc(Math.random() * (CERTAINTIES.length - 2))];
			lines[i].push(entity + category + cert);
		}
	}

	return lines;
};