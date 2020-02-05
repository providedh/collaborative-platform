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
		obj.subscribe('ui/loaded', ()=>{
			_setupLegend()
			_updateLegendVisibility(true);
		});

		obj.currentValues = {};
		obj.entityTypeOptions = {
			'ingredient': [],
			'utensil': [],
			'productionMethod': []
		};

		_setupUI();

		document.getElementById('editor')
			.setAttribute('using-recipes-plugin', _getSettings()['usingRecipesPlugin']);
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
		/*
		const annotation_left_col = document.getElementById('uncertainty-tab').children[0].children[2],
			input = _createEntityTypeInput('annotation');
		annotation_left_col.appendChild(input);
		*/

		// 5) add certainty asserted value
		const ref_asserted_value = document.getElementById('uncertainty-tab').children[1].children[1],
			ref_input = _createEntityTypeInput('ref-certainty');
		ref_asserted_value.appendChild(ref_input);		

		// 6) add handler for settings change
		document.getElementById('using-recipes-plugin').addEventListener('change', _handleSettingsChange);

		// 7) setup forms
		_updateEntitySelectOptions();
		document.getElementById('using-recipes-plugin').addEventListener('change', _updateEntitySelectOptions);
		document.getElementById('locus').addEventListener('change', _updateAssertedValueSelectOptions);
	}

	function _getInputId(name){
		const creatingNewTypeCheckboxId = `${name}-tei-add-type`,
			creatingNewType = document.getElementById(creatingNewTypeCheckboxId).checked,
			inputId = creatingNewType===true?`${name}-type-name`:`${name}-entity-type`;
		return inputId;		
	}

	function _getUsingId(name){
		return `${name}-tei-use-type`;
	}

	function _getFormId(name){
		return name + '-entity-type-form-group';
	}

	function _createLegendEntries(styles){
		function _createEntityLegendEntry(entity){
		    const entry = (
		      `<span class="teiLegendElement recipeLegendEntry">
		        <span class="color bg-${entity[0]}"></span> 
		        <i class="fas" id="legend-${entity[0]}"></i>
		        ${entity[0].slice(0,1).toUpperCase() + entity[0].slice(1)}
		      </span>`);

		    document.getElementById('ui-style').innerText += `
		        #legend-${entity[0]}::before {
		          content: "${entity[1].icon}";
		        }\n
		      `;

		    return entry;
		}
		const legendEntries = styles
			.map(s=>_createEntityLegendEntry(s))
			.map(html=>$.parseHTML(html)[0]);

		return legendEntries;
	}

	function _setupLegend(){
		const entities = ['ingredient', 'utensil', 'productionMethod'],
			styles = entities.map(e=>[e, ColorScheme.scheme.entities[e]]);

		let extraLegend = _createLegendEntries(styles),
			legend = document.getElementById('top-legend').getElementsByTagName('ul')[0];
		extraLegend.forEach(e=>legend.appendChild(e));

		extraLegend = _createLegendEntries(styles);
		legend = document.getElementById('legend').getElementsByTagName('ul')[0];
		extraLegend.forEach(e=>legend.appendChild(e));
	}

	function _updateLegendVisibility(usingRecipesPlugin){
		if(usingRecipesPlugin === true){
			Array.from(document.getElementsByClassName('recipeLegendEntry')) //extra legend tags
				.forEach(x=>x.classList.remove('hidden'));
		}else{
			Array.from(document.getElementsByClassName('recipeLegendEntry')) //extra legend tags
				.forEach(x=>x.classList.add('hidden'));
		}
	}

	function _createEntityTypeInput(name){
		const inputHtml = `<div id="${name}-entity-type-form-group" class="entityTypeFormGroup" fromList="true">
			  <label class="form-check-label useNewTypeLabel" for="${name}-tei-use-type">
			    <span class="type"></span> don't want to specify it? Close this control
			    </label>
			  <input class="form-check-input useNewType" type="checkbox" value="" id="${name}-tei-use-type">

			  <label class="form-check-label addNewTypeLabel" for="${name}-tei-add-type">
			    <span class="type"></span> not in the list?
			    Add new <span class="type"></span>
			    </label>
			  <input class="form-check-input addNewType" type="checkbox" value="" id="${name}-tei-add-type">

			  <div class="typeList">
			    <label for="${name}-entity-type">Reference
			      <span class="help-tooltip" help="Select a type for the TEI selected entity.<br/>This 
			      is only available for ingredient, utensil and productionMethod entities" />
			    </label>
			    <select class="form-control form-control-sm" id='${name}-entity-type'></select>
			  </div>
			  <div class="newType">
			    <label for="${name}-type-name">New entity name
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

		self.XML_EXTRA_CHAR_SPACER = args.XML_EXTRA_CHAR_SPACER;

		Array.from(divNodes).forEach(div=>{
			if(div.attributes.hasOwnProperty('type')){
				const type = div.attributes['type'].value;
				if(self.entityTypeOptions.hasOwnProperty(type)){
					const options = Array
						.from(div.getElementsByTagName('object'))
						.filter(x=>x.attributes.hasOwnProperty('id'))
						.map(x=>[x.textContent, x.attributes['id'].value]);
					self.entityTypeOptions[type] = options;
				}
			}
		});

		_styleRecipeEntities();

		_updateInputOptions();
	}

	function _updateAnnotationTypeInput(){
		let show = true;

		show = show && self.currentValues['locus'] == 'value';
		show = show && ['ingredient', 'utensil', 'productionMethod'].includes(self.currentValues['tag-name']);
		show = show && self.currentValues['attribute-name'] == 'ref';
		show = show && _getSettings()['usingRecipesPlugin'];

		if(show === true){
			document.getElementById(_getFormId('ref-certainty'))
				.classList.remove('d-none');
			document.getElementById('uncertainty-tab').children[1].children[1].children[0].classList.add('d-none');
			document.getElementById('uncertainty-tab').children[1].children[1].children[1].classList.add('d-none');
		}else{
			document.getElementById(_getFormId('ref-certainty'))
				.classList.add('d-none');
			document.getElementById('uncertainty-tab').children[1].children[1].children[0].classList.remove('d-none');
			document.getElementById('uncertainty-tab').children[1].children[1].children[1].classList.remove('d-none');
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

	function _createEntitiesFormOptions(){
		const usingRecipesPlugin = _getSettings()['usingRecipesPlugin'];
		const entities = Object
				.keys(ColorScheme.scheme['entities'])
				.filter(e=>!['ingredient', 'utensil', 'productionMethod'].includes(e) || usingRecipesPlugin);

	    const options = entities.map(e=>$.parseHTML(
	      `<option value="${e}">${e.slice(0,1).toUpperCase() + e.slice(1)}</option>`
	      )[0]);

	    return options;
	}

	function _updateAssertedValueSelectOptions(){
		const select_form = document
	    	.getElementById('asserted-value');
	    if(select_form.tagName.toLowerCase() == 'select'){
	    	select_form.innerHTML = '';
	    	_createEntitiesFormOptions().forEach(opt=>select_form.appendChild(opt));
	    }
	}

	function _updateEntitySelectOptions(){    
	    let select_form = document
	      .getElementById('asserted-value-input-options')
	      .getElementsByTagName('select')[0];
	    select_form.innerHTML = '';
	    _createEntitiesFormOptions().forEach(opt=>select_form.appendChild(opt));

	    select_form = document
	      .getElementById('tag-name');
	    select_form.innerHTML = '';
	    _createEntitiesFormOptions().forEach(opt=>select_form.appendChild(opt));

	    select_form = document
	      .getElementById('tei-tag-name');
	    select_form.innerHTML = '';
	    _createEntitiesFormOptions().forEach(opt=>select_form.appendChild(opt));

	    _updateAssertedValueSelectOptions();
	}
	
	function _handleOptionsChange(currentValues){
		self.currentValues = currentValues;

		_updateAnnotationTypeInput();
		_updateTeiTypeInput();

		if(
			currentValues.modifiedField == 'tag-name' ||
			currentValues.modifiedField == 'tei-tag-name'){
			_updateInputOptions();
		}
	}

	function _handleSettingsChange(e){
		const usingRecipesPlugin = e.target.checked;
		document.getElementById('editor')
			.setAttribute('using-recipes-plugin', usingRecipesPlugin);

		_updateLegendVisibility(usingRecipesPlugin);

		if(usingRecipesPlugin === false){
			document.getElementById(_getFormId('ref-certainty'))
				.classList.add('d-none');
			
			document.getElementById(_getFormId('tei'))
				.classList.add('d-none');
		}else{
			_updateTeiTypeInput();
			_updateAnnotationTypeInput();
		}
	}

	function _getInputValue(type){
		const usingInput = document.getElementById(_getUsingId(type)),
			input = document.getElementById(_getInputId(type)),
			value = input.value.startsWith(self.XML_EXTRA_CHAR_SPACER)? 
					input.value.slice(self.XML_EXTRA_CHAR_SPACER.length):
					input.value;
		return (usingInput.checked===false)?value:null;
	}
	
	function _handleAnnotationCreate(json){
		const {usingRecipesPlugin} = _getSettings();

		if(usingRecipesPlugin === true){
			if(json.hasOwnProperty('locus')){
				// annotating uncertainty
				if(['ingredient', 'utensil', 'productionMethod'].includes(json['tag']) &&
					json['attribute_name'] == 'ref'){
						json['asserted_value'] = _getInputValue('ref-certainty');
				}
			} else {
				// annotating tei
				const asserted_value = _getInputValue('tei');
					
				if(['ingredient', 'utensil', 'productionMethod'].includes(json['tag']) && asserted_value != null){
					json['asserted_value'] = asserted_value
					json['attribute_name'] = 'ref';
					json['locus'] = 'value';
				}
			}
		}
		
		console.log('sent > ',JSON.stringify(json));
		self.publish('recipesWebsocket/send', JSON.stringify(json));
	}
	
	function _getSettings(){
		return {
			usingRecipesPlugin: document.getElementById('using-recipes-plugin').checked
		};
	}

	function _getValues(){}

	function _createInputOptions(entityType){
		const option2html = ([name, value])=>`<option value=${value}>${name[0].toUpperCase() + name.slice(1)}</option>`;
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

		if(self.currentValues['locus'] == 'value'
				&& ['ingredient', 'utensil', 'productionMethod'].includes(self.currentValues['tag-name'])
				&& self.entityTypeOptions.hasOwnProperty(self.currentValues['tag-name'])){
			_populateInputOptions('ref-certainty', self.currentValues['tag-name']);
		}
	}

	function _createStyles4Entities(){
		const borderRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`#editor[using-recipes-plugin="true"] object[type="${e[0]}"]{ border-color: ${e[1].color};}`)
	      .join('\n');

	    const entityFillRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`#editor[using-recipes-plugin="true"] object.bg-${e[0]}{ background-color: ${e[1].color};}`)
	      .join('\n');

	    const entityIconRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`div#annotator-root[display-annotations="true"] 
		      	#editor[using-recipes-plugin="true"]
		      	object[type="${e[0]}"]::before{ content: "${e[1].icon}";}`)
	      .join('\n');

	    const entityIconColorRules = Object
	      .entries(ColorScheme.scheme['entities'])
	      .map(e=>`div#annotator-root[color-annotations="true"]
		      	#editor[using-recipes-plugin="true"]
		      	object[type="${e[0]}"]::before{ color: ${e[1].color};}`)
	      .join('\n');

	    return [
	      borderRules,
	      entityFillRules,
	      entityIconRules,
	      entityIconColorRules,
	    ].join('\n');
	}

	function _createStyles4Ref(entity){
		function _createStyles(ref){
		    const colorRule = `
		      div#annotator-root[color-annotations="false"] #editor[using-recipes-plugin="true"] objectName[ref="${ref}"]
		      {
		          border-color: lightgrey !important;
		      }
		    `
		    const displayRule = `
		      div#annotator-root[display-annotations="true"] #editor[using-recipes-plugin="true"] objectName[ref="${ref}"]::before
		      {
		          content:"";
		          position: absolute;
		          font-size: 0.7em;
		          padding-top: 1.3em;
		          color:grey;
		          font-family: "Font Awesome 5 Free";
		          font-weight: 900;
		          min-width: 5em;
		      }
		    `
		    const hideRule = `
		      div#annotator-root[display-annotations="false"] #editor[using-recipes-plugin="true"] objectName[ref="${ref}"]
		      {
		          border-color: white !important;
		      }
		    `
		    const tagRule = `
		      #editor[using-recipes-plugin="true"] objectName[ref="${ref}"]
		      {
		          border-bottom: solid 2px white;
		          cursor: default;
		          background-color: white;
		          display: inline-block;
		          height: 1.7em;
		          position: relative;
		      }
		    `

		    const borderRules = `#editor[using-recipes-plugin="true"] objectName[ref="${ref}"]{ border-color: ${entity[1].color};}`;

		    const entityIconRules = `div#annotator-root[display-annotations="true"] #editor[using-recipes-plugin="true"] objectName[ref="${ref}"]::before{ content: "${entity[1].icon}";}`

		    const entityIconColorRules = `div#annotator-root[color-annotations="true"] #editor[using-recipes-plugin="true"] objectName[ref="${ref}"]::before{ color: ${entity[1].color};}`

		    return [
		      colorRule,
		      displayRule,
		      hideRule,
		      tagRule,
		      borderRules,
		      entityIconRules,
		      entityIconColorRules,
		    ].join('\n');
		}

		const styles = $(`object[type="${entity[0]}"]`).toArray().map(node=>{
			const ref = '#'+node.id.slice(self.XML_EXTRA_CHAR_SPACER.length),
				selector = `#editor[using-recipes-plugin="true"]  objectName[ref="${ref}"]`;

			return _createStyles(ref);
		}).join('\n');

	    return styles;
	}

	function _styleRecipeEntities(){
		document.getElementById('recipes-style').innerHTML = '';
		document.getElementById('recipes-style').innerHTML += _createStyles4Entities();
		document.getElementById('recipes-style').innerHTML += 
			_createStyles4Ref(['ingredient', ColorScheme.scheme.entities['ingredient']]);
		document.getElementById('recipes-style').innerHTML += 
			_createStyles4Ref(['utensil', ColorScheme.scheme.entities['utensil']]);
		document.getElementById('recipes-style').innerHTML += 
			_createStyles4Ref(['productionMethod', ColorScheme.scheme.entities['productionMethod']]);
	}
	
	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default RecipesPlugin;
