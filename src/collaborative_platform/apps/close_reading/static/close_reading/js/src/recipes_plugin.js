/* Module: RecipesPlugin
 * Module covering the needed functionality for interacting with 
 * recipes in the annotator. It handles all the additional UI rendering,
 * event handling, and new annotation creation.
 * 
 * In order to use it, replace the event that websockets listens to to 
 * 'recipesWebsocket/send' in
 * sub.subscribe('websocket/send', json=>websocket.send(json));
 *
 * This module adds a new tab in the top panel, and an entity type form input.
 *
 * Publishes:
 * - recipesWebsocket/send
 *
 * Listens:
 * - panel/load_history
 * - panel/reset
 * - panel/autocomplete_options
 * */
import AjaxCalls from './utilities/ajax.js';
import ColorScheme from './utilities/color.js';

let RecipesPlugin = function(args){
	let self = null;
	const ajaxCalls = AjaxCalls();

	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

		obj.subscribe('websocket/send', _handleAnnotationCreate);
		obj.subscribe('panel/update', _handleOptionsChange);
		obj.subscribe('document/render', _handleDocumentRender);

		obj.currentValues = {};
		obj.entityTypeOptions = {
			'ingredient': [],
			'utensil': [],
			'productionMethod': []
		};

		_setupUI();

		document.getElementById('editor')
			.setAttribute('usingRecipePlugin', _getSettings()['usingRecipesPlugin']);
		/*
			obj.subscribe('panel/load_history', _handleLoadHistory);
			obj.subscribe('panel/reset', _handlePanelReset);
			obj.suscribe('panel/autocomplete_options', _handleAutocompleteOptions);
			obj.subscribe('sidepanel/selection', _handleSidepanelSelection);
			obj.subscribe('document/selection', _handleDocumentSelection);
		*/

		self = obj;
		return obj;
	}

	function _setupUI(){
		// 1) add style tag
		document.getElementsByTagName('head')[0].appendChild(_createStyleTag());

		// 2) add tab for settings
		document.getElementById('tab-controls').appendChild(_createSettingsToggle());
		document.getElementById('annotation-form').appendChild(_createSettingsTab());

		// 3) add entity input to annotation tab
		const tei_first_col = document.getElementById('tei-tab').children[0].children[0],
			col = $.parseHTML('<div class="col"></div>')[0];
		col.append(_createEntityTypeInput('tei'));
		tei_first_col.insertAdjacentElement('afterend', col);

		// 4) add entity input to tei tab
		const annotation_left_col = document.getElementById('uncertainty-tab').children[0].children[2],
			input = _createEntityTypeInput('annotation');
		annotation_left_col.appendChild(input);

		// 5) add handler for settings change
		document.getElementById('using-recipes-plugin').addEventListener('change', _handleSettingsChange);

		// 6) style objects according to their type
		_styleRecipeEntities();
	}

	function _getInputId(name){
		const creatingNewTypeCheckboxId = `${name}-tei-add-type`,
			creatingNewType = document.getElementById(creatingNewTypeCheckboxId).checked,
			inputId = creatingNewType===true?`${name}-type-name`:`${name}-entity-type`;
		return inputId;		
	}

	function _getFormId(name){
		return name + '-entity-type-form-group';
	}

	function _createEntityTypeInput(name){
		const inputHtml = `<div id="${name}-entity-type-form-group" class="entityTypeFormGroup" fromList="true">
			  <label class="form-check-label addNewTypeLabel" for="teiAddType">
			    <span class="type"></span> not in the list?
			    Add new <span class="type"></span>
			    </label>
			  <input class="form-check-input addNewType" type="checkbox" value="" id="${name}-tei-add-type">
			  <div class="typeList">
			    <label for="${name}-entity-type">Type
			      <span class="help-tooltip" help="Select a type for the TEI selected entity.<br/>This 
			      is only available for ingredient, utensil and productionMethod entities" />
			    </label>
			    <select class="form-control form-control-sm" id='${name}-entity-type'></select>
			  </div>
			  <div class="newType">
			    <label for="${name}-type-name">New <span class="type"></span> entity name
			      <span class="help-tooltip" help="Provide a name for a new TEI entity type.<br/>This is
			      only available for ingredient, utensil and productionMethod entities." />
			    </label>
			    <input class="form-control" type="text" id="${name}-type-name">
			  </div>
			</div>
		`
		return $.parseHTML(inputHtml)[0];
	}

	function _createSettingsToggle(){
		const toggleHtml = `<li class="nav-item">
				<a id="settings" 
						class="nav-link" 
						data-toggle="tab" 
						href="#settings-tab" 
						role="tab" 
						aria-controls="settings-tab" 
						aria-selected="false">
					Settings
				</a>
			</li>`
		return $.parseHTML(toggleHtml)[0];
	}

	function _createSettingsTab(){
		const tabHtml = `<div class="tab-pane" id="settings-tab" role="tabpanel" aria-labelledby="settings">
              	<div class="form-row"><div class="col">
              		<label class="form-check-label" for="using-recipes-plugin">Use recipes module</label>
					  <input checked class="form-check-input addNewType" type="checkbox" value="" id="using-recipes-plugin">
              	</div>
              	<div class="col"><p>Configure the close reading app.</p></div>
              	</div>
            </div>`
		return $.parseHTML(tabHtml)[0];
	}

	function _createStyleTag(){
		const tagHtml = '<style type="text/css" id="recipes-style"></style>';
		return $.parseHTML(tagHtml)[0];
	}

	function _handleDocumentRender(args){
		const editor = document.getElementById('editor'),
			divNodes = editor.getElementsByTagName('div');

		Array.from(divNodes).forEach(div=>{
			if(div.attributes.hasOwnProperty('type')){
				const type = div.attributes['type'].value;
				if(self.entityTypeOptions.hasOwnProperty(type)){
					const options = Array
						.from(div.getElementsByTagName('object'))
						.filter(x=>x.attributes.hasOwnProperty('type'))
						.map(x=>x.attributes['type'].value);
					self.entityTypeOptions[type] = options;
				}
			}
		});

		_updateInputOptions();
	}

	function _updateAnnotationTypeInput(){
		let show = true;

		show = show && self.currentValues['locus'] == 'name';
		show = show && ['ingredient', 'utensil', 'productionMethod'].includes(self.currentValues['asserted-value']);
		show = show && _getSettings()['usingRecipesPlugin'];

		if(show === true){
			document.getElementById(_getFormId('annotation'))
				.classList.remove('d-none');
		}else{
			document.getElementById(_getFormId('annotation'))
				.classList.add('d-none');
		}
	}

	function _updateTeiTypeInput(){
		let show = true;

		show = show && ['ingredient', 'utensil', 'productionMethod'].includes(self.currentValues['tei-tag-name']);
		show = show && _getSettings()['usingRecipesPlugin'];

		if(show === true){
			document.getElementById(_getFormId('tei'))
				.classList.remove('d-none');
		}else{
			document.getElementById(_getFormId('tei'))
				.classList.add('d-none');
		}
	}
	
	function _handleOptionsChange(currentValues){
		self.currentValues = currentValues;

		_updateAnnotationTypeInput();
		_updateTeiTypeInput();

		if(currentValues.modifiedField == 'asserted-value' || 
			currentValues.modifiedField == 'tei-tag-name'){
			_updateInputOptions();
		}
	}

	function _handleSettingsChange(e){
		const useRecipesPlugin = e.target.checked;
		document.getElementById('editor')
			.setAttribute('usingRecipePlugin', useRecipesPlugin);

		if(useRecipesPlugin === false){
			document.getElementById(_getFormId('annotation'))
				.classList.add('d-none');
			document.getElementById(_getFormId('tei'))
				.classList.add('d-none');
		}else{
			_updateTeiTypeInput();
			_updateAnnotationTypeInput();
		}
	}
	
	function _handleAnnotationCreate(json){
		const annotationInput = document.getElementById(_getInputId('annotation')),
			teiInput = document.getElementById(_getInputId('tei'));

		console.log(annotationInput, teiInput)

		self.publish('recipesWebsocket/send', json)
	}
	
	function _getSettings(){
		return {
			usingRecipesPlugin: document.getElementById('using-recipes-plugin').checked
		};
	}

	function _getValues(){}

	function _createInputOptions(entityType){
		const option2html = option=>`<option value=${option}>${option[0].toUpperCase() + option.slice(1)}</option>`;
		const html2node = html=>$.parseHTML(html)[0];

		return self.entityTypeOptions[entityType].map(option=>html2node(option2html(option)));
	}

	function _populateInputOptions(input_name, entity){
		const input = document.getElementById(_getInputId(input_name)),
			options = _createInputOptions(entity);

		input.innerHTML = '';
		options.forEach(option=>input.appendChild(option));
	}

	function _updateInputOptions(){
		if(self.currentValues['tei-tag-name'] != undefined
				&& self.entityTypeOptions.hasOwnProperty(self.currentValues['tei-tag-name'])){
			_populateInputOptions('tei', self.currentValues['tei-tag-name']);
		}

		if(self.currentValues['locus'] == 'name'
				&& self.currentValues['asserted-value'] != undefined
				&& self.entityTypeOptions.hasOwnProperty(self.currentValues['asserted-value'])){
			console.log('annotation', self.currentValues['asserted-value'])
			_populateInputOptions('annotation', self.currentValues['asserted-value']);
		}
	}

	function _createStyles4Entities(entityNode){
		const borderRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`#editor[usingRecipePlugin="true"] object[type="${e[0]}"]{ border-color: ${e[1].color};}`)
	      .join('\n');

	    const entityFillRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`#editor[usingRecipePlugin="true"] object.bg-${e[0]}{ background-color: ${e[1].color};}`)
	      .join('\n');

	    const entityIconRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`div#annotator-root[display-annotations="true"] 
		      	#editor[usingRecipePlugin="true"]
		      	object[type="${e[0]}"]::before{ content: "${e[1].icon}";}`)
	      .join('\n');

	    const entityIconColorRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`div#annotator-root[color-annotations="true"]
		      	#editor[usingRecipePlugin="true"]
		      	object[type="${e[0]}"]::before{ color: ${e[1].color};}`)
	      .join('\n');

	    return [
	      borderRules,
	      entityFillRules,
	      entityIconRules,
	      entityIconColorRules,
	    ].join('\n');
	}

	function _createStyles4EntityDiv(entityNode){
		const borderRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`#editor[usingRecipePlugin="true"] div[type="${e[0]}"] object{ border-color: ${e[1].color};}`)
	      .join('\n');

	    const entityFillRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`#editor[usingRecipePlugin="true"] div[type="${e[0]}"] object{ background-color: ${e[1].color};}`)
	      .join('\n');

	    const entityIconRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`div#annotator-root[display-annotations="true"] 
		      	#editor[usingRecipePlugin="true"]
		      	div[type="${e[0]}"] object::before{ content: "${e[1].icon}";}`)
	      .join('\n');

	    const entityIconColorRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`div#annotator-root[color-annotations="true"]
		      	#editor[usingRecipePlugin="true"]
		      	div[type="${e[0]}"] object::before{ color: ${e[1].color};}`)
	      .join('\n');

	    return [
	      borderRules,
	      
	      entityIconRules,
	      entityIconColorRules,
	    ].join('\n');
	}

	function _styleRecipeEntities(){
		document.getElementById('recipes-style').innerHTML = _createStyles4Entities();
		document.getElementById('recipes-style').innerHTML = _createStyles4EntityDiv();
	}
	
	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default RecipesPlugin;
