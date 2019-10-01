/* Module: Annotator
 * Module for handling the load of files, creation of annotations, and saving
 * of files.
 *
 * Publishes:
 * - none
 *
 * Listens:
 * - annotator/create
 * - annotator/save
 * - annotator/load
 * */

import AjaxCalls from './utilities/ajax.js';
import Alert from './utilities/alert.js';

var Annotator = function(args){
	let self = null;
	let _selection = null;
	let ajaxCalls = AjaxCalls();

	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

		obj.subscribe('annotator/create-tei', _handleCreateTEIAnnotation);
		obj.subscribe('annotator/create-uncertainty', _handleCreateUncertaintyAnnotation);
		obj.subscribe('annotator/save', _handleFileSave);
		obj.subscribe('document/selection', _handleDocumentSelection);

		self = obj;
		return obj;
	}

	function _handleCreateTEIAnnotation(args){
		if(_selection == null)
	        return

	    self.publish('websocket/send', JSON.stringify({
	    	'start_pos': _selection.abs_positions.start,
	    	'end_pos': _selection.abs_positions.end,
	    	'tag': args['tei-tag-name']
	    }));
	}

	function _handleCreateUncertaintyAnnotation(args){
		if(_selection == null)
	        return

	    const data = {
	    	'start_pos': _selection.abs_positions.start,
	    	'end_pos': _selection.abs_positions.end,
	    	"category": args.category,
            "locus": args.locus,
            "certainty": args['cert-level'],
            "description": args.desc,
            "tag": args['tag-name'],
	    };

        if(args['locus'] == 'value'){
	    	data['asserted_value'] = args['asserted-value'];
        }

        if(args['locus'] == 'name'){
            data['tag'] = args['asserted-value'];
        }

        if(args['attribute_name'] != ''){
        	data['locus'] = 'attribute';
            data['attribute_name'] = args['attribute-name'];
            data['asserted_value'] = args['asserted-value'];
        }
        
        if(args['attribute-name'] == 'sameAs' && ['person', 'event', 'org', 'place'].includes(args['tag-name']) && args['references'] != ''){
            data['asserted_value'] = args['references-filepath']+'#'+args['asserted-value'];
        }

        console.log(data)

	    self.publish('websocket/send', JSON.stringify(data));
	}

	function _handleFileSave(args){
		ajaxCalls.safeFile(window.project_id, window.file_id).then(response=>{
			if(response.success === true){
				Alert.alert('success','Changes successfully saved.');
				document.getElementById('versionLink').innerText = 'Version: '+response.content.version;
				window.file_version = response.content.version;
				self.publish('file/saved', response.content.version);
			}
			else
				Alert.alert('success','Error saving the changes.');
			console.info('Changes '+(response.success === true)?'saved':'not saved');
		});
	}

	function _handleDocumentSelection(args){
		_selection = args.selection;
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default Annotator;
