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
import ColorScheme from './aux/color.js';

var DocumentView = function(args){
	let self = null;
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
            ids_replaced_xml = file.replace(/xml:id="/gm,'id="'+XML_EXTRA_CHAR_SPACER),
            body_replaced_xml = ids_replaced_xml.replace(/body>/gm, 'page>'), // Creating a separate div would alter structure
            parsed_tei = $.parseXML(body_replaced_xml).documentElement,
            body = parsed_tei.getElementsByTagName('page')[0];
        
	        self.TEItext = file;
	        self.TEIbody = body.innerHTML.replace(' xmlns="http://www.tei-c.org/ns/1.0"', '');
	        self.TEIemptyTags = body.innerHTML.match(/<[^>]+\/>/gm);
	        self.TEIheaderLength = file.indexOf('<body>') + '<body>'.length;
	        body.setAttribute('size', 'A4');
	        
	        return({body, parsed_tei});
	}

	function _styleAnnotatedTags(file){
		function addStyle(id, category, cert){
		    const greyRule = 'div#annotator-root[display-uncertainty=true] ' 
		        + '#'+id
		        + '{background-color: lightgrey;}';
		    const colorRule = 'div#annotator-root[display-uncertainty=true][color-uncertainty=true] ' 
		        + '#'+id
		        + `{background-color: ${ColorScheme.calculate(category,cert)};}`;

		    document.getElementById('style').innerText += (greyRule);
    		document.getElementById('style').innerText += (colorRule);
		}

		document.getElementById('style').innerText = '';

		Array.from(file.getElementsByTagName('teiHeader')[0].getElementsByTagName('certainty'), a=>a)
            .forEach(annotation=>{
                annotation.attributes['target'].value.trim().split(" ").forEach(target=>{
                    const node = document.getElementById(XML_EXTRA_CHAR_SPACER+target.slice(1));
                    if(node != null){   
                        addStyle(
                            XML_EXTRA_CHAR_SPACER+target.slice(1), 
                            annotation.attributes['category'].value, 
                            annotation.attributes['cert'].value
                            );
                    }
                })
            });
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

	    const selection_range = selection.getRangeAt(0);

	    let start_content = _contentsFromRange($('#editor page')[0], 0, selection_range.startContainer,selection_range.startOffset),
	        end_content = _contentsFromRange($('#editor page')[0], 0, selection_range.endContainer,selection_range.endOffset);

	    for(let empty_tag of self.TEIemptyTags){
	        start_content = start_content.replace(_expandedEmptyTag(empty_tag), empty_tag);
	        end_content = end_content.replace(_expandedEmptyTag(empty_tag), empty_tag);
	    }

	    const positions = [];

	    for(let i=0; i<start_content.length; i++){
	        if(self.TEIbody[i]!=start_content[i]){
	            positions.push(self.TEIheaderLength + i);
	            break;
	        }
	    }

	    for(let i=0; i<end_content.length; i++){
	        if(self.TEIbody[i]!=end_content[i]){
	            positions.push(self.TEIheaderLength + i);
	            break;
	        }
	    }

	    const abs_positions = {start: Math.min(...positions), end: Math.max(...positions)};

	    selection = {text:text, range:selection_range, abs_positions:abs_positions};
		
		self.publish('document/selection', selection);
	}

	function _handleDocumentLoad(file){
		const {body, parsed_tei} = _parseTEI(file);
		document.getElementById('editor').innerHTML='';
		document.getElementById('editor').appendChild(body);
		_styleAnnotatedTags(parsed_tei);
		self.publish('document/render', {});
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
