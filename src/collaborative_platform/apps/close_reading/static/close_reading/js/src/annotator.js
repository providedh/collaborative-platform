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

import AjaxCalls from './aux/ajax.js';

var Annotator = function(args){
	let self = null;
	let _selection = null;
	let ajax_urls = AjaxCalls();

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
	    console.log(args)
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

        if(args['locus'] == 'attribute'){
            data['attribute_name'] = args['attribute-name'];
            data['asserted_value'] = args['asserted-value'];
        }

        if(args['locus'] == 'attribute' && ['person', 'event', 'org', 'place'].includes(args['tag-name']) && args['references'] != ''){
            data['references'] = args.references
        }


        console.log(data)

	    self.publish('websocket/send', JSON.stringify(data));
	}

	function _handleFileSave(args){
		$.ajax({
	        url:ajax_urls.get_save_url(window.project_id, window.file_id),
	        type: 'PUT',   //type is any HTTP method
	        data: {},      //Data as js object
	        success: function (a) {
	            console.log('save - success < ',ajax_urls.get_save_url(window.project_id, window.file_id),' < ',a);
	        },
	        error: function (a) {
	            console.log('save - error < ',ajax_urls.get_save_url(window.project_id, window.file_id),' < ',a)
	        }
	    })
	}

	function _handleDocumentSelection(selection){
		_selection = selection;
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default Annotator;
