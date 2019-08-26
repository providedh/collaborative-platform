/* Module: ColorScheme
 * Utility methods for retrieving the color scheme 
 * or calculating the color for a specific annotation
 *
 * */
var ColorScheme = function(args){
	let self = null;

	const _colorScheme = {
	    ignorance : {
	        unknown : '#e2dce8',
	        low : '#c7b7d3',
	        medium : '#aa95bb',
	        high : '#9270a8',
	    },
	    imprecision : {
	        unknown : '#fbf3d4',
	        low : '#f6e7a9',
	        medium : '#f2dd8f',
	        high : '#f1d155',
	    },
	    credibility : {
	        unknown : '#f1d9d4',
	        low : '#ebb1a6',
	        medium : '#d87c6f',
	        high : '#cc4c3b',
	    },
	    incompleteness : {
	        unknown : '#dceaea',
	        low : '#bbd7d5',
	        medium : '#9bc4c1',
	        high : '#67b2ac',
	    }
	};

	function _applyColorScheme(source, level){
		if(_colorScheme.hasOwnProperty(source) &&
			_colorScheme[source].hasOwnProperty(level))
				return _colorScheme[source][level];
		else
			return '#fff';
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return {
		schemes: _colorScheme,
		calculate: _applyColorScheme
	};
};

export default ColorScheme;