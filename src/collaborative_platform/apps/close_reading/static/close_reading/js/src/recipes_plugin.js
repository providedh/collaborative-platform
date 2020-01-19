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

		_setupUI();
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
	}

	function _getInputId(name){
		const creatingNewTypeCheckboxId = `${name}-tei-add-type`,
			creatingNewType = document.getElementById(creatingNewTypeCheckboxId).checked,
			inputId = creatingNewType===true?`${name}-type-name`:`${name}-entity-type`;
		return inputId;		
	}

	function _createEntityTypeInput(name){
		const inputHtml = `<div class="entityTypeFormGroup" fromList="true">
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
              	<div class="form-row"><div class="col"></div>
              		<div class="col"><p>Configure the close reading app.</p></div>
              	</div>
            </div>`
		return $.parseHTML(tabHtml)[0];
	}

	function _createStyleTag(){
		const tagHtml = '<style type="text/css" id="recipes-style"></style>';
		return $.parseHTML(tagHtml)[0];
	}

	function _handleDocumentLoad(){}
	function _handleOptionsChange(){}
	function _handleSettingsChange(){}
	
	function _handleAnnotationCreate(json){
		const annotationInput = document.getElementById(_getInputId('annotation')),
			teiInput = document.getElementById(_getInputId('tei'));

		console.log(annotationInput, teiInput)

		//self.publish('recipesWebsocket/send', json)
	}
	
	function _getSettings(){}
	function _getValues(){}

	function _createInputElements(){}
	function _createInputOptions(){}
	function _populateInputElements(){}
	function _updateInputElements(){}

	function _createStyles4Entity(){}
	function _styleRecipeEntities(){}
	function _styleRecipeLists(){}

	function _getRecipeEntities(){}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default RecipesPlugin;
