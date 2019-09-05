/* Module: HistoryView
 * Module for displaying the document history.
 *
 * Publishes:
 * - none
 *
 * Listens:
 * - panel/display_options
 * */
import AjaxCalls from './utilities/ajax.js';

var HistoryView = function(args){
	let self = null;
	let ajaxCalls = AjaxCalls();

	let versions = [
	];

	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

		const history_div = document.getElementById('history'),
			history_container = document.getElementById('history-container');

		history_div.addEventListener('mouseover', 
			e=>history_div.classList.add('hovered'));

		history_container.addEventListener('mouseleave', 
			e=>history_div.classList.remove('hovered'));

		ajaxCalls.getHistory(window.project_id, window.file_id, window.file_version).then(response=>{
			if(response.success === true){
				versions = response.content.data;
				_updateVersions();
			}
		});


		//obj.suscribe('popup/render', _handleRenderPopup);

		self = obj;
		return obj;
	}

	function _renderVersions(){
		const client_width = document
			.getElementById('versions')
			.getBoundingClientRect().width - 10;

		const getTimestamp = date=>date.getTime()+10000*date.getHours()+100*date.getMinutes();

		const dates = versions.map(t=>getTimestamp(new Date(t.timestamp))),
			min = Math.min(...dates),
			max = Math.max(1, Math.max(...dates) - min);

		for(let version of versions){
			const date = new Date(version.timestamp),
				timestamp = getTimestamp(date),
				offset = client_width * (timestamp-min) / max;

			const element = document.createElement('a');
	        element.setAttribute('class','version');
	        element.setAttribute('href',version.url);
	        element.style.setProperty('left', `${offset}px`);

	        if(version.version == +window.file_version)
	        	element.style.setProperty('background-color', '#00b3b0');

	        element.addEventListener('mouseenter', 
	        	evt=>_handleVersionHoverIn(evt,version));
	        element.addEventListener('mouseout', 
	        	evt=>_handleVersionHoverOut(evt,version));

	        console.info('Retrieved version', version.timestamp)

	        document.getElementById('versions').appendChild(element);
		}
	}

	function _handleVersionHoverIn(evt, timestamp){
	    const popup = document.getElementById('history-popup');
	    const max = Math.max(timestamp.imprecision,timestamp.incompleteness,
	        timestamp.ignorance,timestamp.credibility, timestamp.variation),
	        xScale = d=>6*d/max;

	    popup.innerHTML=`
	      Version ${timestamp.version}<br>
	      ${(new Date(timestamp.timestamp)).toUTCString()}<br>
	      Contributor : ${timestamp.contributor}<br>
	      <div class="content">
	      <span>
	        Imprecision<br/>
	        Incompleteness<br/>
	        Credibility<br/>
	        Ignorance<br/>
	      </span>
	      <span>
	        <span class="color uncertainty" author="me" title="high"
	            style="width:${xScale(timestamp.imprecision)}em;" category="imprecision" cert="high"></span></br>
	        <span class="color uncertainty" author="me" title="high" 
	            style="width:${xScale(timestamp.incompleteness)}em;" category="incompleteness" cert="high"></span></br>
	        <span class="color uncertainty" author="me" title="high" 
	            style="width:${xScale(timestamp.ignorance)}em;" category="ignorance" cert="high"></span></br>
	        <span class="color uncertainty" author="me" title="high" 
	            style="width:${xScale(timestamp.credibility)}em;" category="credibility" cert="high"></span></br>
	      </span>
	      <span>
	        ${timestamp.imprecision}</br> 
	        ${timestamp.incompleteness}</br> 
	        ${timestamp.ignorance}</br> 
	        ${timestamp.credibility}</br>
	      </span>
	      </div>
	    `;
	    popup.style.left = evt.target.style.left;
	    popup.style.setProperty('display','block');
	}

    /*<span class="color variation" author="me" title="high" 
	        ${timestamp.variation}
        style="width:${xScale(timestamp.variation)}em;" category="variation" cert="high"></span></br>*/

	function _handleVersionHoverOut(event, timestamp){
	    document.getElementById('history-popup').style.setProperty('display','none');
	}

	function _updateVersions(){
		document.getElementById('versions').innerHTML = '';
		_renderVersions();
	}

	function _renderHistoryGraph(){

	}

	function _updateGraph(){

	}

	function _displayPopup(args){
		_notimplemented('_displayPopup')();
	}

	function _hidePopup(args){
		_notimplemented('_hidePopup')();
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default HistoryView;
