const defaultConfig = [
    {name: 'barDirection', type: 'selection', value: 'Horizontal', params: {
    	options: [
    		'Horizontal',
    		'Vertical'
    	]}
    },
    {name: 'dimension', type: 'selection', value: 'entityType', params: {
    	options: [
	    	'Number of entities per document',
	    	'Number of entities per type',
            'Most common entities',
	    	'Number of annotations per document',
	    	'Number of annotations per category',
	    	"Frequency for an attribute's values",
	    	'Frequency for most common attribute values',
    	]}
    },
    {name: 'renderOverlay', type: 'toogle', value: false},
];

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {barDirection, dimension, renderOverlay} = currentValues;

	const configOptions = [
		{name: 'barDirection', type: 'selection', value: barDirection, params: {
			options: [
				'Horizontal',
				'Vertical'
			]}
		},
		{name: 'dimension', type: 'selection', value: dimension, params: {
			options: [
		    	'Number of entities per document',
		    	'Number of entities per type',
		        'Most common entities',
		    	'Number of annotations per document',
		    	'Number of annotations per category',
		    	"Frequency for an attribute's values",
		    	'Frequency for most common attribute values',
			]}
		},
		{name: 'renderOverlay', type: 'toogle', value: renderOverlay},
    ];


    if(renderOverlay === true){
    	const overlay = currentValues.hasOwnProperty('overlay')?currentValues[0]:'Certainty level';
    	configOptions.push(
		    {name: 'overlay', type: 'selection', value: overlay, params: {
		    	options: [
		    		'Certainty level',
		    		'Author',
		    		'Time of last edit'
		    	]}
		    }
    	);
    }

	return configOptions;
}