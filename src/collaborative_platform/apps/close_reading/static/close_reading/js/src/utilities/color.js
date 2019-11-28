/* Module: ColorScheme
 * Utility methods for retrieving the color scheme 
 * or calculating the color for a specific annotation
 *
 * */
import teiConf from './taxonomy.js';

var ColorScheme = (function(args){
	let self = null;

	const certaintyLevelTransparencies = {
		high: 'ff',
		medium: 'b8',
		low: '5e',
		unknown: '30'
	};

	function _applyColorScheme(source, level){
		if(teiConf['taxonomy'] &&
			certaintyLevelTransparencies.hasOwnProperty(level))
				return teiConf['taxonomy'][source]['color'] + certaintyLevelTransparencies[level];
		else
			return '#fff';
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return {
		calculate: _applyColorScheme
	};
})();

export default ColorScheme;