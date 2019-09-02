/* Module: Popup
 * Module for displaying customizable popups.
 *
 * Publishes:
 * - none
 *
 * Listens:
 * - panel/display_options
 * */
var Popup = function(args){
	let self = null;

	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

		obj.subscribe('popup/render', _displayPopup);
		obj.subscribe('popup/hide', _handleHidePopup);

		self = obj;
		return obj;
	}

	function _displayPopup(args){
		const values = Object.assign({
			title: 'The title',
			subtitle: 'The subtitle',
			body: 'The body',
			x: '50%',
			y: '25%'
		},args);

		console.log(values)

		document
        	.getElementById('popup')
        	.getElementsByClassName('card-title')[0]
        	.innerHTML = values.title;

        document
        	.getElementById('popup')
        	.getElementsByClassName('card-subtitle')[0]
        	.innerHTML = values.subtitle;

        document
        	.getElementById('popup')
        	.getElementsByClassName('card-text')[0]
        	.innerHTML = values.body;

        document.getElementById('popup').style.setProperty('left',args.x);
		document.getElementById('popup').style.setProperty('top',args.y);

		document.getElementById('popup').style.setProperty('display','initial');
	}

	function _hidePopup(args){
		document.getElementById('popup').style.setProperty('display','none');
	}

	function _handleRenderPopup(args){_displayPopup(args);}

	function _handleHidePopup(args){_hidePopup(args);}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

/* Module: Tooltips
 * Module for displaying customizable tooltips on document elements.
 *
 * Publishes:
 * - none
 *
 * Listens:
 * - document/load
 * */
var Tooltips = function(args){
	let self = null;
	const tags = [
		'placeName','place','country','location','geogName',
		'geolocation','person','name','persName','occupation',
		'event','object','date','time','org','pb','rolename'
		]

	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

		obj.subscribe('document/render', _handleDocumentLoad);

		self = obj;
		return obj;
	}

	function _handleDocumentLoad(args){
		for(let tag of tags){
			Array.from(document.getElementsByTagName(tag)).forEach(node=>{
				node.addEventListener('mouseenter', ()=>self.publish('popup/render',{
					title: (`<span class="teiLegendElement" id="${tag}">
							<span class="color" id=""></span></span>`
							+ node.textContent),
					subtitle: `( ${tag} )`,
					body: '',
					x: (node.getBoundingClientRect().x+node.getBoundingClientRect().width/2 -150)+'px', 
					y: (node.getBoundingClientRect().y+40)+'px'
				}));
				node.addEventListener('mouseout', ()=>self.publish('popup/hide',{}));
			});
		}
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export {Popup, Tooltips};
