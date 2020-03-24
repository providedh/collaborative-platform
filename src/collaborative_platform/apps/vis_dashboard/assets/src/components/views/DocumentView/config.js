export default function getOptions(form){
	const documentNames = Object.values(window.documents).map(x=>x.name),
		defaultConfig = [
	    {name: 'syncWithViews', type: 'toogle', value: false},
	    {name: 'documentId', type: 'selection', value: Object.keys(window.documents)[0], params: {options: Object.keys(window.documents), labels: documentNames}}
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
		const documentId = currentValues.hasOwnProperty('documentId')?currentValues.document:Object.keys(window.documents)[0];
	    configOptions.push({name: 'documentId', type: 'selection', value: documentId, params: {options: Object.keys(window.documents), labels: documentNames}});
	}

	return configOptions;
}