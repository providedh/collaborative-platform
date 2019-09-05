/* Module: Alert
 * Module for showing alerts
 *
 * */
var Alert = (function(args){
	const _node = document.getElementById('alert');

	function _alert(type, message){
		_node.innerText = message;
		_node.setAttribute('class', 'alert show alert-'+type);
		setTimeout(()=>_node.setAttribute('class', 'alert hide alert-'+type), 3000);
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return {alert: _alert};
})();

export default Alert;