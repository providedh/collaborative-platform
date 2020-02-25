const defaultConfig = [
    {name: 'tileLayout', type: 'selection', value: 'Regular', params: {
    	options: [
    		'Regular',
    		'Split',
            'Tilted',
    	]}
    },
    {name: 'colorScale', type: 'selection', value: 'Red and blue', params: {
    	options: [
    		'Red and blue',
    		'Spectral',
    		'Blues'
    	]}
    },
    {name: 'rangeScale', type: 'selection', value: 'Linear', params: {
        options: [
            'Linear',
            'Logarithmic',
            'Power'
        ]}
    },
    {name: 'dimension', type: 'selection', value: 'Entities related by documents', params: {
    	options: [
	    	'Entities related by documents',
	    	'Documents related by entities',
    	]}
    },
];

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {tileLayout, colorScale, rangeScale, dimension} = currentValues;

	const configOptions = [
	    {name: 'tileLayout', type: 'selection', value: tileLayout, params: {
	    	options: [
	    		'Regular',
	    		'Split',
	            'Tilted',
	    	]}
	    },
	    {name: 'colorScale', type: 'selection', value: colorScale, params: {
	    	options: [
	    		'Red and blue',
	    		'Spectral',
	    		'Blues'
	    	]}
	    },
	    {name: 'rangeScale', type: 'selection', value: rangeScale, params: {
	        options: [
	            'Linear',
	            'Logarithmic',
	            'Power'
	        ]}
	    },
	    {name: 'dimension', type: 'selection', value: dimension, params: {
	    	options: [
		    	'Entities related by documents',
		    	'Documents related by entities',
	    	]}
	    },
	];

	return configOptions;
}