/* Module: DocumentView
 * Module for loading and controlling events of XML files.
 *
 * Publishes:
 * - document/selection
 * - document/hover
 * - annotator/save
 *
 * Listens:
 * - panel/display_options
 * */
import CertaintyStyler from './utilities/certaintystyling.js';
import AjaxCalls from './utilities/ajax.js';

var DocumentView = function(args){
	let self = null;
	const ajaxCalls = AjaxCalls();
	const XML_EXTRA_CHAR_SPACER="xxxx"; // Used to keep string lengths for ids.

	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

		document.getElementById('editor').onmouseup = 
      		document.getElementById('editor').onselectionchange = 
      			()=>_handleSelection();

		obj.subscribe('document/load', _handleDocumentLoad);

		//obj.publish('document/selection', {});
		//obj.publish('document/render', {});
		//obj.publish('document/hover', {});
		//obj.publish('annotator/load', {});
		//
		// Add listener for input updates
		//document
		//	.getElementById('in')
		//	.addEventListener('selection', e=>_handleTextSelection(e));

		self = obj;
		return obj;
	}

	function _parseTEI(file){
		const sanityzed_xml = file.replace(/\r/gm," "),
			// xml:id is not valid as an attribute name for DOM queries
            ids_replaced_xml = file.replace(/xml:id="/gm,'id="'+XML_EXTRA_CHAR_SPACER),

            // Add a page element so that browsers add there a xmlns="http://www.tei-c.org/ns/1.0" attribute
            // instead of changing the original and rendered content
            body_open_replaced_xml = ids_replaced_xml.replace(/<body>/, '<body><page xmlns="http://www.tei-c.org/ns/1.0">'), 
            body_replaced_xml = body_open_replaced_xml.replace(/<\/body>/, '<\/page><\/body>'), 

            parsed_tei = $.parseXML(body_replaced_xml).documentElement,
            body = parsed_tei.getElementsByTagName('body')[0];
        
	        self.TEItext = file;
	        self.TEIbody = body.innerHTML
	        self.TEIemptyTags = body.innerHTML.match(/<[^>]+\/>/gm) || [];
	        self.TEIheaderLength = file.indexOf('<body>') +'<body>'.length;
	        body.setAttribute('size', 'A4');
	        
	        return({body, parsed_tei});
	}

	function _expandedEmptyTag(empty_tag){
	    const tag_name = empty_tag.match(/[^ ,<,/,>]+/gm)[0],
	        opening_tag = empty_tag.replace('/>','>'),
	        closing_tag = '</'+tag_name+'>';

	    return opening_tag + closing_tag;
	}

	function _contentsFromRange(startNode, startOffset, endNode, endOffset){
	    const selection = document.createRange();

	    selection.setStart(startNode, startOffset);
	    selection.setEnd(endNode,endOffset);

	    const fragment = selection.cloneRange().cloneContents(),
	        container = document.createElement('div');

	    container.appendChild(fragment);

	    return container.innerHTML;
	}

	function _handleSelection(){
        let text = "", selection, node = null;

	    if (window.getSelection) {
	        selection = window.getSelection();
	        text = selection.toString();
	    }else if (document.selection && document.selection.type != "Control"){
	        selection = document.selection;
	        text = document.selection.createRange().text;
	    }

	    if(selection.isCollased === true)
	    	return

	    const selection_range = selection.getRangeAt(0);

	    let start_content = _contentsFromRange($('#editor page')[0], 0, selection_range.startContainer,selection_range.startOffset),
	        end_content = _contentsFromRange($('#editor page')[0], 0, selection_range.endContainer,selection_range.endOffset);


	    for(let empty_tag of self.TEIemptyTags){
	        start_content = start_content.replace(_expandedEmptyTag(empty_tag), empty_tag);
	        end_content = end_content.replace(_expandedEmptyTag(empty_tag), empty_tag);
	    }

	    /* Browsers will now add the xmlns attribute nonetheless to
	       make sure that the markup is representative of the namespaces.
	       This breaks the ability to compare with the initial content. 
	    */
	    const positions = [];

	    // Remove the extra page element added to keep the TEI namespace
	    const original_text = self.TEIbody.replace('<page xmlns="http://www.tei-c.org/ns/1.0">', '');

	    for(let i=0; i<start_content.length; i++){
	        if(original_text[i]!=start_content[i]){
	            positions.push(self.TEIheaderLength + i);
	            break;
	        }
	    }

	    for(let i=0; i<end_content.length; i++){
	        if(original_text[i]!=end_content[i]){
	            positions.push(self.TEIheaderLength + i);
	            break;
	        }
	    }

	    const abs_positions = {start: Math.min(...positions), end: Math.max(...positions)};

	    selection = {text:text, by_id: false, range:selection_range, abs_positions:abs_positions};
		
		self.publish('document/selection', {selection});
	}

	function _handleDocumentLoad({xml_content, certainties}){
		const {body, parsed_tei} = _parseTEI(xml_content);
		document.getElementById('editor').innerHTML='';
		document.getElementById('editor').appendChild(body);

		console.log(certainties)

		ajaxCalls.getUser().then(response=>{
			let user = 'none';
			if(response.success === true)
				user = response.content.id;

			//_styleAnnotatedTags(parsed_tei, user);
			self.publish('document/render', {XML_EXTRA_CHAR_SPACER, user, document: parsed_tei});
		})
	}

	function _handleDisplayOptions(args){
		_notimplemented('_handleDisplayOptions')();
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default DocumentView;
