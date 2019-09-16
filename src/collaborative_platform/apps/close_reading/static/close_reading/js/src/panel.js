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
import AjaxCalls from './utilities/ajax.js';

let PanelView = function(args){
	let self = null;
	const ajaxCalls = AjaxCalls();
	let values = {};
	let currentFocus;

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
		obj.subscribe('document/selection', _handleDocumentSelection);

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
		document.getElementById('saveFile')
			.addEventListener('click', ()=>obj.publish('annotator/save',{}));

		document.getElementById('references-autocomplete').addEventListener('input', e=>{
	        const tag = values['tag-name'];
	        document.getElementById('references').value = e.target.value;
	        if(values['attribute-name'] == 'sameAs' &&
	            ['person', 'event', 'org', 'place'].includes(tag)){
	            _updateAutocompleteOptions(tag.replace('org','organization'), e.target.value);
	        }
	    })

	    document.getElementById("references-autocomplete").options = [];
	    _setup_autocomplete(document.getElementById("references-autocomplete"));

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

        input.id = 'asserted-value';

        input.addEventListener('change', ()=>_handleValueChange('asserted-value', input.value));

        const asserted_value_container = document.getElementById('asserted-value-container');
        asserted_value_container.removeChild(asserted_value_container.children[0]);
        asserted_value_container.appendChild(input);

        if(values['locus'] == 'name')
        	document.getElementById('tag-name-input').style.setProperty('display','none');
        else
        	document.getElementById('tag-name-input').style.setProperty('display','initial');

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
			'cert-level': document.getElementById('cert-level').value,
			'category': document.getElementById('category').value,
			'locus': document.getElementById('locus').value,
			'tag-name': document.getElementById('tag-name').value,
			'attribute-name': document.getElementById('attribute-name').value,
			'category': document.getElementById('category').value,
			'asserted-value': document.getElementById('asserted-value-container').getElementsByClassName('input')[0].value,
			'references': document.getElementById('references').value,
			'description': document.getElementById('description').value,
			'tei-tag-name': document.getElementById('tei-tag-name').value,
		};
		return options;
	}

	function _setup_autocomplete(inp) {
	        //Snippet from w3school.com	     
	        inp.addEventListener("input", function(e) {
	              let a, b, i, val = inp.value;
	        closeAllLists();
	        if (!val) { return false;}
	        currentFocus = -1;
	        a = document.createElement("DIV");
	        a.setAttribute("id", "autocomplete-list");
	        a.setAttribute("class", "autocomplete-items");
	        document.getElementById('references-container').appendChild(a);
	        for (let i = 0; i < inp.options.length; i++) {
	            if (inp.options[i].name.substr(0, val.length).toUpperCase() == val.toUpperCase()) {
	              b = document.createElement("DIV");
	              b.data = inp.options[i];
	              b.innerHTML = "<strong>" + inp.options[i].name.substr(0, val.length) + "</strong>";
	              b.innerHTML += inp.options[i].name.substr(val.length);
	              b.innerHTML += ` | ${inp.options[i].filepath}`;
	              b.innerHTML += "<input type='hidden' id='"+inp.options[i].id+"' value='" + 
	                `${inp.options[i].name} | ${inp.options[i].filepath}`; + "'>";
	              b.addEventListener("click", function(e) {
	                  document.getElementById('references').value = this.data.name;
	                  inp.value = `${this.data.name} | ${this.data.filepath}`;
	                  document.getElementById('proposedValue').value = this.data.id;
	                  closeAllLists();
	              });
	              a.appendChild(b);
	            }
	        }
	      });

	      inp.addEventListener("keydown", function(e) {
	          let x = document.getElementById("autocomplete-list");
	          if (x) x = x.getElementsByTagName("div");
	          if (e.keyCode == 40) {
	            currentFocus++;
	            addActive(x);
	          } else if (e.keyCode == 38) { //up
	            currentFocus--;
	            addActive(x);
	          } else if (e.keyCode == 13) {
	            e.preventDefault();
	            if (currentFocus > -1) {
	              if (x) x[currentFocus].click();
	            }
	          }
	      });
	      function addActive(x) {
	        if (!x) return false;
	        removeActive(x);
	        if (currentFocus >= x.length) currentFocus = 0;
	        if (currentFocus < 0) currentFocus = (x.length - 1);
	        x[currentFocus].classList.add("autocomplete-active");
	      }
	      function removeActive(x) {
	        for (let i = 0; i < x.length; i++) {
	          x[i].classList.remove("autocomplete-active");
	        }
	      }
	      function closeAllLists(elmnt) {
	        let x = document.getElementsByClassName("autocomplete-items");
	        for (let i = 0; i < x.length; i++) {
	          if (elmnt != x[i] && elmnt != inp) {
	            x[i].parentNode.removeChild(x[i]);
	          }
	        }
	      }
	      document.addEventListener("click", function (e) {
	          closeAllLists(e.target);
	      });
	    }

	function _updateAutocompleteOptions(entityType, text){
		ajaxCalls.getAutocomplete(window.project_id, entityType, text).then(response=>{
			if(response.success === true){				
				document.getElementById("references-autocomplete").options = response.content.data.map(a=>(
	                {name: a._source.name, id:a._source.id, filepath:a._source.filepath}
	            ))
	            _updateAutocompleteInput(document.getElementById("references-autocomplete"));
			}
	        else
	        	console.log('autocomplete - error < ',window.project, entityType, text,' < ',response)
		});
	}

	function _updateAutocompleteInput(inp){
	    currentFocus = -1;
	    let a = document.getElementById('autocomplete-list');
	    for (let i = 0; i < inp.options.length; i++) {
	        if (inp.options[i].name.toUpperCase().includes(inp.value.toUpperCase())) {
	          let b = document.createElement("DIV");
	          b.data = inp.options[i];
	          b.innerHTML = "<strong>" + inp.options[i].name.substr(0, inp.value.length) + "</strong>";
	          b.innerHTML += inp.options[i].name.substr(inp.value.length);
	          b.innerHTML += ` | ${inp.options[i].filepath}`;
	          b.innerHTML += "<input type='hidden' id='"+inp.options[i].id+"' value='" + 
	            `${inp.options[i].name} | ${inp.options[i].filepath}` + "'>";
	          b.addEventListener("click", function(e) {
	              document.getElementById('references').value = this.data.name;
	              inp.value = `${this.data.name} | ${this.data.filepath}`;
	              document.getElementById('asserted-value').value = this.data.id;
	              closeAllLists();
	          });
	          a.appendChild(b);
	        }
	    }
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
		if(['locus', 'attribute-name'].includes(id))
			_updateReferencesControl();
		
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

	function _handleDocumentSelection(args){
		document.getElementById('selection').value = args.selection.text;
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default PanelView;
