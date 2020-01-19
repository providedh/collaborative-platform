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

	function _setupUI(){}

	function _getInputId(name){
		const creatingNewTypeCheckboxId = `${name}-tei-add-type`,
			creatingNewType = document.getElementById(creatingNewTypeCheckboxId).checked,
			inputId = creatingNewType===true?`${name}-type-name`:`${name}-entity-type`;
		return inputId;		
	}

	function _createEntityTypeInput(name){}

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
