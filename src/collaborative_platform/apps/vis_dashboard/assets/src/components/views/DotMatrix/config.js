const defaultConfig = [
    {name: 'singleSource', type: 'toogle', value: false},
    {name: 'dataSourceType', type: 'selection', value: 'Regular', params: {
    	options: [
    		'File',
    		'Folder',
            'Author',
    	]}
    },
    {name: 'dotType', type: 'selection', value: 'Entity', params: {
        options: [
            'Entity',
            'Annotation',
        ]}
    },
    {name: 'colorBy', type: 'selection', value: 'Type', params: {
    	options: [
	    	'Type',
	    	'Author',
    	]}
    },
];

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {singleSource, dataSourceType, dotType, colorBy} = currentValues;
	const dataSource = currentValues.hasOwnProperty('dataSource')?currentValues.dataSource:null;

	const configOptions = [
	    {name: 'singleSource', type: 'toogle', value: singleSource},
	    {name: 'dataSourceType', type: 'selection', value: dataSourceType, params: {
	    	options: [
	    		'File',
	    		'Folder',
	            'Author',
	    	]}
	    },
	];

	if(singleSource === true){
		let sources = ['file_1', 'file_2', 'file_3', 'file_11', 'file_12', 'file_13'];
		if(dataSourceType == 'Folder')
			sources = ['folder_1', 'folder_2', 'folder_3'];
		if(dataSourceType == 'Author')
			sources = ['author_1', 'author_3'];

		const value = sources.includes(dataSource)?dataSource:sources[0];

		configOptions.push(
		    {name: 'dataSource', type: 'selection', value: value, params: {
		    	options: sources}
		    }
		);
	}

	const entities = ['Person', 'Place', 'Ingredient'];
	const dotTypes = ['Entity', 'Annotation', ...entities];

	configOptions.push(
	    {name: 'dotType', type: 'selection', value: dotType, params: {
	        options: dotTypes}
	    }
	);

	const entityParams = {
		Person: ['age', 'surname', 'nme', 'organization'],
		Place: ['country', 'geolocation', 'population'],
		Ingredient: ['type', 'isVegetable']
	}

	let colorByOptions = [];
	if(dotType == 'Annotation')
		colorByOptions = ['Author', 'Category', 'Level', 'Locus', 'Target type'];
	else if(dotType == 'Entity')
		colorByOptions = ['author', 'type'];
	else
		colorByOptions = entityParams[dotType]
	
	const colorByValue = colorByOptions.includes(colorBy)?colorBy:colorByOptions[0];

	configOptions.push(
	    {name: 'colorBy', type: 'selection', value: colorByValue, params: {
	    	options: colorByOptions}
	    }
	);

	return configOptions;
}