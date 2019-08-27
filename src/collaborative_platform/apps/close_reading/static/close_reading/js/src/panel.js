/* Module: PanelView
 * View controlling visuals and events for the top panel.
 *
 * Publishes:
 * - parameter/change
 * - annotator/create
 * - annotator/save
 * - popup/render
 * - annotator/load
 * - panel/display_options
 *
 * Listens:
 * - panel/load_history
 * - panel/reset
 * - panel/autocomplete_options
 * */
var PanelView = function(args){
	let self = null;
	let values = {};

	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

		obj.suscribe('panel/load_history', _handleLoadHistory);
		obj.suscribe('panel/reset', _handlePanelReset);
		obj.suscribe('panel/autocomplete_options', _handleAutocompleteOptions);

		Object.assign(values, _getCurrentValues());
		_updatePanelControls();

		document.getElementById('visual-options').getElementsByTagName('a');

		// Add event listeners for form value changes
		const formInputs = document.getElementById('annotation-form').getElementsByTagName('input');
		const formSelects = document.getElementById('annotation-form').getElementsByTagName('select');

		Array.from(formInputs)
			.map(e=>e.addEventListener('change',
				()=>_handleValueChange(e.attributes['id'].value, e.value))); // 
		Array.from(formSelects)
			.map(e=>e.addEventListener('change',
				()=>_handleValueChange(e.attributes['id'].value, e.value))); // 

		//obj.publish('parameter/change', {});
		//obj.publish('annotator/create', {});
		//obj.publish('annotator/save', {});
		//obj.publish('popup/render  ', {});
		//obj.publish('annotator/load', {});
		//obj.publish('panel/display_options', {});
		//
		// Add listener for input updates
		/*document
			.getElementById('in')
			.addEventListener('change', e=>_handleInputChange(e));*/

		obj.getValues = ()=>_getValues;

		self = obj;
		return obj;
	}

	function _updatePanelControls(){
        const input = $('#asserted-value-input-options [locus='+values['locus']+']')[0];
        $("#asserted-value-container").html(input.outerHTML);
        $("#asserted-value-container .input").attr('id','proposedValue');
        if(values['locus'] == 'attribute')
        	document.getElementById('attribute-name-input').style.setProperty('display','initial');
        else
        	document.getElementById('attribute-name-input').style.setProperty('display','none');

		if(values['locus'] == 'attribute' 
				&& ['person', 'event', 'org', 'place'].includes(values['tag-name'])
				&& values['attribute-name'] == 'sameAs'){
			document.getElementById('references-container').style.setProperty('display','initial');
		}else{
			document.getElementById('references-container').style.setProperty('display','none');
		}
	}

	function _handleValueChange(id, value){
		values[id] = value;
		_updatePanelControls();
		console.log(id,value);
	}

	function _getValues(){
		return values;
	}

	function _getCurrentValues(args){
		const options = {
			'annotating-uncertainty': document
				.getElementById('annotating-uncertainty')
				.attributes['class']
				.value
				.includes('active'),
			'annotating-tei': document
				.getElementById('annotating-tei')
				.attributes['class']
				.value
				.includes('active'),
			'category': document.getElementById('category').value,
			'locus': document.getElementById('locus').value,
			'tag-name': document.getElementById('tag-name').value,
			'attribute-name': document.getElementById('attribute-name').value,
			'category': document.getElementById('category').value,
			'asserted-value': document.getElementById('asserted-value').value,
			'references': document.getElementById('references').value,
			'description': document.getElementById('description').value,
			'tei-tag-name': document.getElementById('tei-tag-name').value,
		};
		return options;
	}

	function _handleLoadHistory(args){
		_notimplemented('_handleLoadHistory')();
	}

	function _handlePanelReset(args){
		Object.assign(values, _getCurrentValues());
	}

	function _handleAutocompleteOptions(args){
		_notimplemented('_handleAutocompleteOptions')();
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default PanelView;
