const PixelCorpusSortBy = {
	mostSelfContributedFirst: 'mostSelfContributedFirst',
	leastSelfContributedFirst: 'leastSelfContributedFirst',
	lastEditedFirst: 'lastEditedFirst',
	lastEditedLast: 'lastEditedLast',
	higherEntityCountFirst: 'higherEntityCountFirst',
	higherEntityCountLast: 'higherEntityCountLast'
};

const PixelCorpusColorBy = {
	category: 'category',
	certaintyLevel: 'certaintyLevel',
	categoryAndCertaintyLevel: 'categoryAndCertaintyLevel',
	authorship: 'authorship',
	entity: 'entity',
	locus: 'locus'
};

const PixelCorpusSource = {certainty: 'certainty', entities: 'entities'};

const defaultConfig = [
    {name: 'sortDocumentsBy', type: 'selection', value: Object.values(PixelCorpusSortBy)[0], params: {options: Object.values(PixelCorpusSortBy)}},
    {name: 'colorCertaintyBy', type: 'selection', value: Object.values(PixelCorpusColorBy)[0], params: {options: Object.values(PixelCorpusColorBy)}},
    {name: 'source', type: 'selection', value: Object.values(PixelCorpusSource)[0], params: {options: Object.values(PixelCorpusSource)}},
];

export {PixelCorpusSortBy, PixelCorpusColorBy, PixelCorpusSource};

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {sortDocumentsBy, colorCertaintyBy, source} = currentValues;

	const configOptions = [
		{name: 'sortDocumentsBy', type: 'selection', value: sortDocumentsBy, params: {options: Object.values(PixelCorpusSortBy)}},
    	{name: 'colorCertaintyBy', type: 'selection', value: colorCertaintyBy, params: {options: Object.values(PixelCorpusColorBy)}},
    	{name: 'source', type: 'selection', value: source, params: {options: Object.values(PixelCorpusSource)}},
	];

	return configOptions;
}