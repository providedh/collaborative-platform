export default function getOptions(form){
	const documentIds = window.documents.map(x=>x.id),
		documentNames = window.documents.map(x=>x.name),
		defaultConfig = [
	    {name: 'syncWithViews', type: 'toogle', value: false},
	    {name: 'documentId', type: 'selection', value: '44', params: {options: documentIds, labels: documentNames}}
	];

	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {syncWithViews} = currentValues;

	const configOptions = [
	    {name: 'syncWithViews', type: 'toogle', value: syncWithViews},
	];

	if(syncWithViews === false){
		const documentId = currentValues.hasOwnProperty('documentId')?currentValues.documentId:documentIds[0];
	    configOptions.push({name: 'documentId', type: 'selection', value: documentId, params: {options: documentIds, labels: documentNames}});
	}

	return configOptions;
}