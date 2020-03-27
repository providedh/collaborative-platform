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
    {name: 'source', type: 'selection', value: 'entity', params: {
        options: [
            'entity',
            'certainty'
        ]}
    },
    {name: 'axis1', type: 'selection', value: 'documentName', params: {
        options: [
            'id',
            'text',
            'type',
            'documentName',
        ]}
    },
    {name: 'axis2', type: 'selection', value: 'documentName', params: {
        options: [
            'id',
            'text',
            'type',
            'documentName',
        ]}
    },
];

export default function getOptions(form){
	if(form == null)
		return defaultConfig;

	const currentValues = {};
	form.forEach(x=>currentValues[x.name] = x.value);

	const {tileLayout, colorScale, rangeScale, source, axis1, axis2} = currentValues;

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
	    {name: 'source', type: 'selection', value: source, params: {
	        options: [
	            'entity',
	            'certainty'
	        ]}
	    },
	    {name: 'axis1', type: 'selection', value: axis1, params: {
	        options: [
	            'id',
	            'text',
	            'type',
	            'documentName',
	        ]}
	    },
	    {name: 'axis2', type: 'selection', value: axis2, params: {
	        options: [
	            'id',
	            'text',
	            'type',
	            'documentName',
	        ]}
	    },
	];

	return configOptions;
}