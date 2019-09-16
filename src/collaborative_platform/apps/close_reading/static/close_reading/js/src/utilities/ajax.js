/* Module: AjaxCalls
 * Module for building full API call urls.
 *
 * API endpoints:
 * - get_save_url
 * - get_add_annotation_url
 * - get_history_url
 * - get_autocomplete_url
 * */
var AjaxCalls = function(args){
	const base_url = [window.location.protocol + '/', window.location.hostname+':'+window.location.port].join('/');

	const save_url = (project, file) => ['/api','close_reading', 'project', project, 'file', file, 'save/'].join('/');
	const history_url = (project, file, version) => ['/api','close_reading','project', project, 'file', file,'version', version, 'history/'].join('/');
	const search_url = (project, entity_type, query) => ['/api/search/entity_completion/project',project,'entity',entity_type,query].join('/');

	function _init(args){
		const obj = {
			safeFile: (project, file) => _createCall('PUT', base_url + save_url(project, file)),
			getHistory: (project, file, version) => _createCall('GET', base_url + history_url(project, file, version)),
			getAutocomplete: (project, entity_type, query) => _createCall('GET', base_url + search_url(project, entity_type, query))
		};

		return obj;
	}

	function _createCall(method,url){
		function getCookie(name) {
		    let cookieValue = null;
		    if (document.cookie && document.cookie !== '') {
		        const cookies = document.cookie.split(';');
		        for (let i = 0; i < cookies.length; i++) {
		            const cookie = cookies[i].trim();
		            // Does this cookie string begin with the name we want?
		            if (cookie.substring(0, name.length + 1) === (name + '=')) {
		                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		                break;
		            }
		        }
		    }
		    return cookieValue;
		}

		console.log(url)
		const csrftoken = getCookie('csrftoken');

		return new Promise(function(resolve, cancel){
			function csrfSafeMethod(method) {
			    // these HTTP methods do not require CSRF protection
			    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
			}

			$.ajaxSetup({
			    beforeSend: function(xhr, settings) {
			        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			            xhr.setRequestHeader("X-CSRFToken", csrftoken);
			        }
			    }
			});

			$.ajax({
		        url: url,
		        type: method,   //type is any HTTP method
		        data: {},      //Data as js object
		        success: function (a) {
		            resolve({success:true, content:a});
		        },
		        error: function (a) {
		            resolve({success:false, content:a});
		        }
		    })
		})
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default AjaxCalls;
