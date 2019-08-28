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
	    	'asserted_value': args['tei-tag-name'],
	    	'tag': args['tei-tag-name']
	    }));
	}

	function _handleCreateUncertaintyAnnotation(args){
		console.log(ajax_urls.get_add_annotation_url(window.project_id, window.file_id), args, _selection);

		const values = {};
	    Array.from($("#top-panel input"), x=>x).map(i=>values[i.id]=i.value);
	    Array.from($("#top-panel select"), x=>x).map(i=>values[i.id]=i.value);
	    if(values['locus'] == 'value')
	        values['value'] = values['value'];

	    const annotation = (new Annotation()).fromDict(values);
	    
	    // const url = API_urls.get_add_annotation_url(window.project, window.file);
	    const data = {
	            "start_pos": this.selection.abs_positions.start,
	            "end_pos": this.selection.abs_positions.end,
	            "asserted_value": values.proposedValue,
	            "category": "",
	            "locus": "",
	            "certainty": "",
	            "description": "",
	            "tag": values.proposedValue
	        }

	    if(getAnnotatorAttribute('annotation') == 'uncertainty'){
	        Object.assign(data, {
	            "category": values.category,
	            "locus": values.locus,
	            "certainty": values.cert,
	            "asserted_value": values.proposedValue,
	            "description": values.desc,
	            "tag": values['tag-name'],
	            "tag-name": values['tag-name']
	        });

	        if(values['locus'] == 'attribute')
	            data['attribute_name'] = values.attribute_name;

	        if(values['locus'] == 'attribute' && ['person', 'event', 'org', 'place'].includes(values['tag-name']) && values['references'] != ''){
	            data['references'] = values.references
	        }

	        if(values['locus'] == 'name')
	            data['tag'] = values.proposedValue;
	    }

	    console.log(JSON.stringify(data))

	    window.send(JSON.stringify(data));
	}

	function _handleFileSave(args){
		console.log(ajax_urls.get_save_url(window.project_id, window.file_id));
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
