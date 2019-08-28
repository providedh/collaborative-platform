/* Module: PanelView
 * View controlling visuals and events for the top panel.
 *
 * Publishes:
 * - parameter/change
 * - annotator/create-tei
 * - annotator/create-uncertainty
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
		const visualOptions = document.getElementById('visual-options').getElementsByTagName('button');

		Array.from(formInputs)
			.map(e=>e.addEventListener('change',
				()=>_handleValueChange(e.attributes['id'].value, e.value))); // 
		Array.from(formSelects)
			.map(e=>e.addEventListener('change',
				()=>_handleValueChange(e.attributes['id'].value, e.value))); // 
		Array.from(visualOptions)
			.map(e=>e.addEventListener('click', event=>_handleVisualOptionsClick(event)));

		document.getElementById('create-uncertainty-annotation')
			.addEventListener('click', _handleCreateUncertaintyAnnotation);
		document.getElementById('create-tei-annotation')
			.addEventListener('click', _handleCreateTEIannotation);

		obj.getValues = ()=>_getValues;

		self = obj;
		return obj;
	}

	function _updatePanelControls(){
		_updateAssertedValueControl();
		_updateReferencesControl();
	}

	function _updateAssertedValueControl(){
		const input = document
        	.getElementById('asserted-value-input-options')
        	.getElementsByClassName('locus-' + values['locus'])[0]
        	.cloneNode(true);

        input.addEventListener('change', ()=>_handleValueChange('asserted-value', input.value));

        const asserted_value_container = document.getElementById('asserted-value-container');
        asserted_value_container.removeChild(asserted_value_container.children[0]);
        asserted_value_container.appendChild(input);

        if(values['locus'] == 'attribute')
        	document.getElementById('attribute-name-input').style.setProperty('display','initial');
        else
        	document.getElementById('attribute-name-input').style.setProperty('display','none');
	}

	function _updateReferencesControl(){
		if(values['locus'] == 'attribute' 
				&& ['person', 'event', 'org', 'place'].includes(values['tag-name'])
				&& values['attribute-name'] == 'sameAs'){
			document.getElementById('references-container').style.setProperty('display','initial');
		}else{
			document.getElementById('references-container').style.setProperty('display','none');
		}
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

	function _handleCreateTEIannotation(){
		self.publish('annotator/create-tei', _getCurrentValues());
	}

	function _handleCreateUncertaintyAnnotation(){
		self.publish('annotator/create-uncertainty', _getCurrentValues());
	}

	function _handleValueChange(id, value){
		values[id] = value;
		if(id == 'locus')
			_updateReferencesControl();
		if(['locus', 'attribute-name', 'tei-tag-name'].includes(id))
			_updateAssertedValueControl();
		
		console.log(id,value);
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

	function _handleVisualOptionsClick(event){
		const type = event.target.attributes['data-toggle'].value;
		const attribute = event.target.attributes['id'].value;

		if(type == 'collapse'){
			const value = event.target.attributes['aria-expanded'].value;

			document.getElementById('annotator-root').setAttribute(attribute, value);

			if(value == 'false')
				event.target.classList.add('active');
			else
				event.target.classList.remove('active');
		}
		else if(type == 'button'){
			const value = event.target.attributes['aria-pressed'].value;

			document.getElementById('annotator-root').setAttribute(attribute, value=='true'?'false':'true');
		}
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default PanelView;
