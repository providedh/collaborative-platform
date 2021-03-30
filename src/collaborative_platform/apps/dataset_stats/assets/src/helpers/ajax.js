import $ from 'jquery';

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

	const versions_url = (project) => ['/stats', 'project', project, 'versions/'].join('/');
	const stats_url = (project, version) => ['/stats','project', project, 'version', version, 'stats/'].join('/');

	function _init(args){
		const obj = {
			getVersions: (project) => _createCall('PUT', base_url + versions_url(project)),
			getStats: (project, version) => _createCall('GET', base_url + stats_url(project, version)),
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
