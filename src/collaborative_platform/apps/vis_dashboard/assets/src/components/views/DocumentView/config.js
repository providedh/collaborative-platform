export default function getOptions(form){
	const documentNames = Object.values(window.documents).map(x=>x.name),
		defaultConfig = [
		{name: 'showEntities', type: 'toogle', value: true},
		{name: 'showCertainty', type: 'toogle', value: true},
	    {name: 'syncWithViews', type: 'toogle', value: false},
	    {name: 'documentId', type: 'selection', value: Object.keys(window.documents)[0], params: {options: Object.keys(window.documents), labels: documentNames}}
	];

	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {syncWithViews, showEntities, showCertainty} = currentValues;

	const configOptions = [
		{name: 'showEntities', type: 'toogle', value:showEntities},
		{name: 'showCertainty', type: 'toogle', value: showCertainty},
	    {name: 'syncWithViews', type: 'toogle', value: syncWithViews},
	];

	if(syncWithViews === false){
		const documentId = currentValues.hasOwnProperty('documentId')?currentValues.documentId:Object.keys(window.documents)[0];
	    configOptions.push({name: 'documentId', type: 'selection', value: documentId, params: {options: Object.keys(window.documents), labels: documentNames}});
	}

	return configOptions;
}