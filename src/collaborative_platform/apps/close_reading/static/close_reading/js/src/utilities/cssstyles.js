/* Module: CSSstyles
 * Utility methods for retrieving the color scheme 
 * or calculating the color for a specific annotation
 *
 * */
import defConf from './taxonomy.js';

export default function CSSstyles (args){
	let self = null;
	let styleContainerId = null

	function _init(args){
		if(! args.hasOwnProperty('styleContainerId')){ return null; }

		styleContainerId = args['styleContainerId'];

		if(null == document.getElementById(styleContainerId)){
			const head = document.getElementsByTagName('head')[0],
				styleContainer = _createStyleContainer(styleContainerId);
			head.appendChild(styleContainer);
		}
	
		const obj = {}; 
		obj.addRule = _addRule;
		obj.addBeforeRule = _addBeforeRule;
		obj.addAfterRule = _addAfterRule;
		obj.addRuleForId = (id, rule)=>_addRule('#'+id, rule);
		obj.addBeforeRuleForId = (id, rule)=>_addBeforeRule('#'+id, rule);
		obj.addAfterRuleForId = (id, rule)=>_addAfterRule('#'+id, rule);
		obj.resetStyles = _resetStyles;
		obj.createLinearGradient = _createLinearGradient;

		self = obj;
		return obj;
	}

	function _addRule(selector, rule){
		document.getElementById(styleContainerId).innerHTML += `${selector}{${rule}}`;
	}

	function _addBeforeRule(selector, rule){
		document.getElementById(styleContainerId).innerHTML += `${selector}::before{${rule}}`;
	}

	function _addAfterRule(selector, rule){
		document.getElementById(styleContainerId).innerHTML += `${selector}::after{${rule}}`;
	}

	function _resetStyles(){
		document.getElementById(styleContainerId).innerHTML = '';	
	}

	function _createLinearGradient(grad_stops, orientation=0){
		const grad_stops_joined = grad_stops.join(', '), 
			grad =`
				background: -moz-linear-gradient(left, ${grad_stops_joined});
				background: -webkit-gradient(left top, ${grad_stops_joined});
				background: -webkit-linear-gradient(left, ${grad_stops_joined});
				background: -o-linear-gradient(left, ${grad_stops_joined});
				background: -ms-linear-gradient(left, ${grad_stops_joined});
				background: linear-gradient(to right, ${grad_stops_joined});
			`;

		return grad;
	}

	function _createStyleContainer(id){
		const tagHtml = `<style type="text/css" id="${id}"></style>`;
		return $.parseHTML(tagHtml)[0];
	}

	return _init(args);
}