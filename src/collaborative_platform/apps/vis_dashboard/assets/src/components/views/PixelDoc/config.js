const defaultConfig = [
    {name: 'documentId', type: 'selection', value: '#1', params: {options: ['#1', '#2', '#3']}},
    {name: 'dimension', type: 'selection', value: 'entityType', params: {options: ['entityType', 'certaintyType', 'certaintyLevel']}},
];

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {dimension, documentId} = currentValues;

	const configOptions = [
	    {name: 'documentId', type: 'selection', value: documentId, params: {options: ['#1', '#2', '#3']}},
	    {name: 'dimension', type: 'selection', value: dimension, params: {options: ['entityType', 'certaintyType', 'certaintyLevel']}},
	];

	return configOptions;
}