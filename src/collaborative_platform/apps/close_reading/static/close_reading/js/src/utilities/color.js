/* Module: ColorScheme
 * Utility methods for retrieving the color scheme 
 * or calculating the color for a specific annotation
 *
 * */
import defConf from './taxonomy.js';

var ColorScheme = (function(args){
	let self = null;

	const teiConf = Object.assign(defConf, window.preferences);

	const certaintyLevelTransparencies = {
		'very high': 'f0',
		high: 'e0',
		medium: 'c0',
		low: 'a6',
		'very low': '90',
		unknown: '30'
	};

	function _cert2color(source, level){
		if(teiConf['taxonomy'] &&
			teiConf['taxonomy'].hasOwnProperty(source) &&
			certaintyLevelTransparencies.hasOwnProperty(level))
				return teiConf['taxonomy'][source]['color'] + certaintyLevelTransparencies[level];
		else
			return '#fff';
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return {
		calculate: _cert2color,
		scheme: teiConf,

	};
})();

export default ColorScheme;