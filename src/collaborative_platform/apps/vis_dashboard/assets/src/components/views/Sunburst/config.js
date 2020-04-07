import * as d3 from 'd3';

const attributes = {
	entity: {
		options:['id', 'text', 'type', 'documentName'], 
		labels: ['id', 'text', 'type', 'documentName']
	},
	certainty: {
		options: ['resp', 'file', 'category', 'match', 'cert', 'degree'],
		labels: ['author', 'document', 'category', 'attribute', 'certainty', 'degree']
	}
};

const defaultConfig = [
    {name: 'source', type: 'selection', value: 'certainty', params: {
        options: [
            'entity',
            'certainty'
        ]}
    },
    {name: 'numberOfLevels', type: 'selection', value: '3', params: {
        options: d3.range(1, attributes.certainty.options.length).map(x=>x+'')}
    },
    {name: 'level1', type: 'selection', value: 'resp', params: attributes.certainty},
    {name: 'level2', type: 'selection', value: 'file', params: attributes.certainty},
    {name: 'level3', type: 'selection', value: 'category', params: attributes.certainty},
];

function createLevelsControls(numberOfLevels, prevLevels, source){
	const availableOptions = [...attributes[source].options],
		levelValues = d3.range(1, numberOfLevels+1)
		.map(i=>{
			if(Object.hasOwnProperty(prevLevels, 'level'+i)){
				if(Object.hasOwnProperty(attributes[source].options, prevLevels['level'+i])){
					availableOptions.splice(availableOptions.indexOf(prevLevels['level'+i]), 1);
					return prevLevels['level'+i];
				}else{
					return availableOptions.pop();
				}
			}else{
				return availableOptions.pop();
			}
		});
	const levels = levelValues.map((x,i)=>(
		{
			name: 'level'+(i+1), 
			type: 'selection', 
			value: x, 
			params: attributes[source]
	    })
	);

	return levels;
}

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	let {source, numberOfLevels, ...prevLevels} = currentValues;

	numberOfLevels = Math.min(numberOfLevels, attributes[source].length-1);
	const levels = createLevelsControls(numberOfLevels, prevLevels, source);

	const configOptions = [
	    {name: 'source', type: 'selection', value: source, params: {
	        options: [
	            'entity',
	            'certainty'
	        ]}
	    },
	    {name: 'numberOfLevels', type: 'selection', value: numberOfLevels, params: {
	        options: d3.range(1, attributes[source].options.length).map(x=>x+'')}
	    },
	    ...levels
	];

	return configOptions;
}