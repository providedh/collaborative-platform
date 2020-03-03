const defaultConfig = [
    {name: 'syncWithViews', type: 'toogle', value: false},
    {name: 'documentId', type: 'selection', value: '#1', params: {options: ['#1', '#2', '#3']}}
];

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {syncWithViews} = currentValues;

	const configOptions = [
	    {name: 'syncWithViews', type: 'toogle', value: syncWithViews},
	];

	if(syncWithViews === false){
		const documentId = currentValues.hasOwnProperty('documentId')?currentValues.documentId:'#1';
	    configOptions.push({name: 'documentId', type: 'selection', value: documentId, params: {options: ['#1', '#2', '#3']}});
	}

	return configOptions;
}