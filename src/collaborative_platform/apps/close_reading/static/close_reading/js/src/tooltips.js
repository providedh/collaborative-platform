	/* Module: Popup
 * Module for displaying customizable popups.
 *
 * Publishes:
 * - none
 *
 * Listens:
 * - panel/display_options
 * */
import ColorScheme from './utilities/color.js';

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
	const tags = Object.keys(ColorScheme.scheme['entities']);

	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

		Array.from(document.getElementsByClassName('help-tooltip')).forEach(node=>{
				node.addEventListener('mouseenter', e=>self.publish('popup/render',{
					title: '',
					subtitle: '',
					body: node.attributes['help'].value,
					x: (e.clientX - 150)+'px', 
					y: (e.clientY+20)+'px'
				}));
				node.addEventListener('mouseout', ()=>self.publish('popup/hide',{}));
			});

		obj.subscribe('document/render', _handleDocumentLoad);

		self = obj;
		return obj;
	}

	function _handleDocumentLoad(args){
		const certaintyAnnotations = {};

		Array.from(args.document.getElementsByTagName('teiHeader')[0].getElementsByTagName('certainty'), a=>a)
            .forEach(annotation=>{
                annotation.attributes['target'].value.trim().split(" ").forEach(target=>{
                    const id = args.XML_EXTRA_CHAR_SPACER+target.slice(1);
                    if(id != args.XML_EXTRA_CHAR_SPACER && document.getElementById(id) != null){   
                    	certaintyAnnotations[id] = annotation.attributes;
                    }
                })
            });

		for(let tag_name of tags){
			const headerTags = {};

			Array.from(args.document.getElementsByTagName('teiHeader')[0].getElementsByTagName(tag_name), a=>a)
	            .forEach(headerTag=>{
	            	if(headerTag.hasOwnProperty('target'))
		                headerTag.attributes['target'].value.trim().split(" ").forEach(target=>{
		                    const id = args.XML_EXTRA_CHAR_SPACER+target.slice(1);
		                    if(id != args.XML_EXTRA_CHAR_SPACER && document.getElementById(id) != null){   
		                    	certaintyAnnotations[id] = headerTag.attributes;
		                    }
		                })
	            });

			Array.from(document.getElementsByTagName(tag_name)).forEach(node=>{
				const attributes = [], 
					tag_id = node.id,
					original_tag_id = tag_id.startsWith(args.XML_EXTRA_CHAR_SPACER)?
						tag_id.slice(args.XML_EXTRA_CHAR_SPACER.length):
						tag_id;

				attributes.push(...node.attributes);

				if(tag_id != '' && certaintyAnnotations.hasOwnProperty(tag_id))
					attributes.push(...certaintyAnnotations[tag_id]);

				if(tag_id != '' && headerTags.hasOwnProperty(tag_id))
					attributes.push(...headerTags[tag_id]);

				const body = Array
					.from(attributes.filter(x=>x.name != 'id').values())
					.map(e=>e.name+' : '+e.value).join(', <br>');

				const subtitle = original_tag_id != ''?
					`ID : ${original_tag_id}<br/>( ${tag_name} )`:
					`( ${tag_name} )`;

				node.addEventListener('mouseenter', e=>self.publish('popup/render',{
					title: (`<span class="teiLegendElement" id="${tag_name}">
							<span class="color bg-${tag_name}"></span></span>`
							+ node.textContent),
					subtitle: subtitle,
					body: body,
					x: (e.clientX - 150)+'px',//(node.getBoundingClientRect().x+node.getBoundingClientRect().width/2 -150)+'px', 
					y: (e.clientY + 40) +'px'
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
