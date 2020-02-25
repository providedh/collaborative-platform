const defaultConfig = [
    {name: 'backgroundColor', type: 'color', value: '#fff'},
    {name: 'documentId', type: 'documentId', value: '#1'},
    {name: 'dimension', type: 'selection', value: 'two', params: {options: ['content', 'entity', 'certainty']}},
    {name: 'tickets', type: 'multipleSelection', value: ['one','two'], params: {options: ['one', 'two', 'three']}},
    {name: 'gender', type: 'number', value: 21},
    {name: 'periodOfTime', type: 'range', value: 20, params:{ range: [0,100]}},
    {name: 'name', type: 'text', value: ''},
    {name: 'power', type: 'toogle', value: true},
];

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {backgroundColor, documentId, dimension, tickets, gender, periodOfTime, name, power} = currentValues;

	const configOptions = [
	    {name: 'backgroundColor', type: 'color', value: backgroundColor},
	    {name: 'documentId', type: 'documentId', value: documentId},
	    {name: 'dimension', type: 'selection', value: dimension, params: {options: ['content', 'entity', 'certainty']}},
	    {name: 'tickets', type: 'multipleSelection', value: tickets, params: {options: ['one', 'two', 'three']}},
	    {name: 'gender', type: 'number', value: gender},
	    {name: 'periodOfTime', type: 'range', value: periodOfTime, params:{ range: [0,100]}},
	    {name: 'name', type: 'text', value: name},
	    {name: 'power', type: 'toogle', value: power},
	];

	return configOptions;
}