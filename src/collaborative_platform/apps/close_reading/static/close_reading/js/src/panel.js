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

		obj.subscribe('panel/load_history', _handleLoadHistory);
		obj.subscribe('panel/reset', _handlePanelReset);
		obj.suscribe('panel/autocomplete_options', _handleAutocompleteOptions);
		obj.subscribe('sidepanel/selection', _handleSidepanelSelection);
		obj.subscribe('document/selection', _handleDocumentSelection);

		Object.assign(values, _getCurrentValues());
		_updatePanelControls();

		document.getElementById('visual-options').getElementsByTagName('a');

		// Add event listeners for form value changes
		const formInputs = document.getElementById('annotation-form').getElementsByTagName('input');
		const formSelects = document.getElementById('annotation-form').getElementsByTagName('select');
		const visualOptions = document.getElementById('visual-options').getElementsByTagName('button');

		Array.from(formInputs)
			.map(e=>e.addEventListener('input',
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

	    obj.publish('panel/update', _getCurrentValues());

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

        if(values['locus'] == 'name'){
        	document.getElementById('tag-name-input').style.setProperty('display','none');
        	document.getElementById('attribute-name-control').style.setProperty('display','none');
        }
        else{
        	document.getElementById('tag-name-input').style.setProperty('display','initial');
        	document.getElementById('attribute-name-control').style.setProperty('display','initial');
        }
	}

	function _updateReferencesControl(){
		if(['person', 'event', 'org', 'place'].includes(values['tag-name'])
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
		const getAllSelected = selectInput=>Array.from(selectInput.options).reduce((ac,dc)=>dc.selected?[...ac,dc.value]:ac,[]);

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
			'locus': document.getElementById('locus').value,
			'tag-name': document.getElementById('tag-name').value,
			'attribute-name': document.getElementById('attribute-name').value,
			'categories': getAllSelected(document.getElementById('category')),
			'asserted-value': document.getElementById('asserted-value-container').getElementsByClassName('input')[0].value,
			'references': document.getElementById('references').value,
			'references-filepath': document.getElementById('references').filepath,
			'description': document.getElementById('description').value,
			'tei-tag-name': document.getElementById('tei-tag-name').value,
		};

		return options;
	}

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
	
	function closeAllLists(elmnt, inp) {
		let x = document.getElementsByClassName("autocomplete-items");
		for (let i = 0; i < x.length; i++) {
		  if (elmnt != x[i] && elmnt != inp) {
		    x[i].parentNode.removeChild(x[i]);
		  }
		}
	}

	function _setup_autocomplete(inp) {
        inp.addEventListener("input", function(e) {
            let a, b, i, val = inp.value;
	        closeAllLists(null, inp);
	        if (!val) { return false;}
	        currentFocus = -1;
	        a = document.createElement("DIV");
	        a.setAttribute("class", "autocomplete-items");
	        a.setAttribute("id", "autocomplete-list");
	        document.getElementById('references-container').appendChild(a);
	                  
	        for (let i = 0; i < inp.options.length; i++) {
	            if (inp.options[i].name.substr(0, val.length).toUpperCase() == val.toUpperCase()) {
	              b = document.createElement("DIV");
	              b.setAttribute("class", "autocomplete-items");
	              b.data = inp.options[i];
	              b.innerHTML = "<strong>" + inp.options[i].name.substr(0, val.length) + "</strong>";
	              b.innerHTML += inp.options[i].name.substr(val.length);
	              b.innerHTML += ` | ${inp.options[i].filepath}`;
	              b.innerHTML += "<input type='hidden' id='"+inp.options[i].id+"' value='" + 
	                `${inp.options[i].name} | ${inp.options[i].filepath}`; + "'>";
	              b.addEventListener("click", function(e) {
	                  document.getElementById('references').value = this.data.name;
	                  document.getElementById('references').filepath = this.data.filepath;
	                  inp.value = `${this.data.name} | ${this.data.filepath}`;
	                  document.getElementById('asserted-value').value = this.data.id;
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
	      document.addEventListener("click", function (e) {
	          closeAllLists(e.target, inp);
	      });
	    }

	function _updateAutocompleteOptions(entityType, text){
		const inp = document.getElementById("references-autocomplete");
		ajaxCalls.getAutocomplete(window.project_id, entityType, text).then(response=>{
			if(response.success === true){				
				document.getElementById("references-autocomplete").options = response.content.data.map(a=>(
	                {name: a._source.name, id:a._source.id, filepath:a._source.filepath}
	            ))
	            _updateAutocompleteInput(document.getElementById("references-autocomplete"));
			}
	        else{
	        	document.getElementById("references-autocomplete").options = [];
	        	closeAllLists(null, inp);
	        	console.log('autocomplete - error < ',window.project, entityType, text,' < ',response)
	        }
		});
	}

	function _updateAutocompleteInput(inp){
	    currentFocus = -1;
	    let a = document.getElementById('autocomplete-list');
	    for(let child of Array.from(a.children))
	    	a.removeChild(child);

	    for (let i = 0; i < inp.options.length; i++) {
	        if (inp.options[i].name.toUpperCase().includes(inp.value.toUpperCase())) {
	          let b = document.createElement("DIV");
	          b.setAttribute("class", "autocomplete-items");
	          b.data = inp.options[i];
	          const index = inp.options[i].name.toUpperCase().indexOf(inp.value.toUpperCase());

	          b.innerHTML = inp.options[i].name.substr(0,index);
	          b.innerHTML += "<strong>" + inp.options[i].name.substr(index, inp.value.length) + "</strong>";
	          b.innerHTML += inp.options[i].name.slice(index + inp.value.length);
	          b.innerHTML += ` | ${inp.options[i].filepath}`;
	          b.innerHTML += "<input type='hidden' id='"+inp.options[i].id+"' value='" + 
	            `${inp.options[i].name} | ${inp.options[i].filepath}` + "'>";
	          b.addEventListener("click", function(e) {
	    		  closeAllLists(null, inp);
	              document.getElementById('references').value = this.data.name;
	              document.getElementById('references').filepath = this.data.filepath;
	              inp.value = `${this.data.name} | ${this.data.filepath}`;
	              document.getElementById('asserted-value').value = this.data.id;
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
		if(['locus', 'attribute-name', 'tag-name'].includes(id))
			_updateReferencesControl();
		self.publish('panel/update', _getCurrentValues());
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

	function _handleSidepanelSelection(args){
		document.getElementById('selection').value = args.selection.text;
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default PanelView;
