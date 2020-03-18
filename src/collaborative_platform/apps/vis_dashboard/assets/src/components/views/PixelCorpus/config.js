const sortDocumentsByOptions = [
	'mostSelfContributedFirst',
	'leastSelfContributedFirst',
	'lastEditedFirst',
	'lastEditedLast',
	'higherEntityCountFirst',
	'higherEntityCountLast'
	];

const colorCertaintyByOptions = [
	'category',
	'certaintyLevel',
	'categoryAndCertaintyLevel',
	'authorship',
	'entity',
	'locus'
	];

const defaultConfig = [
    {name: 'sortDocumentsBy', type: 'selection', value: sortDocumentsByOptions[0], params: {options: sortDocumentsByOptions}},
    {name: 'colorCertaintyBy', type: 'selection', value: colorCertaintyByOptions[0], params: {options: colorCertaintyByOptions}},
];

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {sortDocumentsBy, colorCertaintyBy} = currentValues;

	const configOptions = [
		{name: 'sortDocumentsBy', type: 'selection', value: sortDocumentsBy, params: {options: sortDocumentsByOptions}},
    	{name: 'colorCertaintyBy', type: 'selection', value: colorCertaintyBy, params: {options: colorCertaintyByOptions}},
	];

	return configOptions;
}