const defaultConfig = [
    {name: 'syncWithViews', type: 'toogle', value: false},
    {name: 'documentId', type: 'selection', value: '44', params: {options: ['44', '45', '43']}}
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
		const documentId = currentValues.hasOwnProperty('documentId')?currentValues.documentId:'44';
	    configOptions.push({name: 'documentId', type: 'selection', value: documentId, params: {options: ['44', '45', '46']}});
	}

	return configOptions;
}