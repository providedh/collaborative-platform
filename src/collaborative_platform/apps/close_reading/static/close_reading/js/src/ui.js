/* Module: UISetup
 * View rendering form options, legends, and other ui 
 * elements based on the taxonomy configuration.
 * */
import ColorScheme from './utilities/color.js';

let UISetup = function(args){
	let self = null;
	
	function _init(args){
		const obj = {
			suscribe: ()=>_notimplemented('suscribe'),
			publish: ()=>_notimplemented('publish'),
		};

		// Add instance to the pub/sub channel
		if(args.hasOwnProperty('channel'))
			args.channel.addToChannel(obj);

    _setupFormControls();
    _setupLegend();
    _setupEntityStyles();

		self = obj;
		return obj;
	}

  function _setupFormControls(){
    
    let select_form = document
      .getElementById('asserted-value-input-options')
      .getElementsByTagName('select')[0];
    _createEntitiesFormOptions().forEach(opt=>select_form.appendChild(opt));

    select_form = document
      .getElementById('tag-name');
    _createEntitiesFormOptions().forEach(opt=>select_form.appendChild(opt));

    select_form = document
      .getElementById('tei-tag-name');
    _createEntitiesFormOptions().forEach(opt=>select_form.appendChild(opt));
  }

  function _createEntitiesFormOptions(){
    const options = Object.entries(ColorScheme.scheme['entities']).map(e=>$.parseHTML(
      `<option value="${e[0]}">${e[0].slice(0,1).toUpperCase() + e[0].slice(1)}</option>`
      )[0]);

    return options;
  }

  function _setupLegend(){
    const legend = document
      .getElementById('legend-sidebar');

    const entityEntries = Object
      .entries(ColorScheme.scheme['entities'])
      .map(e=>_createEntityLegendEntry(e))
      .join('\n');

    const certEntries = Object
      .entries(ColorScheme.scheme['taxonomy'])
      .map(e=>_createCertLegendEntry(e))
      .join('\n');
    
    const legendContent = $.parseHTML(`
      <ul class="nav flex-column">
        <b>Annotation color scheme</b><br/>
        ${entityEntries}
        <b>Uncertainty notion color scheme</b><br/>
        ${certEntries}
      </ul>
      `)[1];
    legend.appendChild(legendContent)
  }

  function _createEntityLegendEntry(entity){
    const entry = (
      `<span class="teiLegendElement">
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

  function _createCertLegendEntry(cert){
    const entry = (
      `<span class="teiLegendElement">
        <span class="color" 
              title="unknown" 
              style="background-color: ${ColorScheme.calculate(cert[0], 'unknown')}">
        </span>
        <span class="color" 
              title="low" 
              style="background-color: ${ColorScheme.calculate(cert[0], 'low')}">
        </span>
        <span class="color" 
              title="medium" 
              style="background-color: ${ColorScheme.calculate(cert[0], 'medium')}">
        </span>
        <span class="color" 
              title="high" 
              style="background-color: ${ColorScheme.calculate(cert[0], 'high')}">
        </span>
        ${cert[0]}
      </span>`);

    return entry;
  }

  function _setupEntityStyles(){
    document.getElementById('ui-style').innerText += _createDisplayStyles();
  }

  function _createDisplayStyles(){
    let selectors = Object.keys(ColorScheme.scheme['entities']).map(e=>
      `div#annotator-root[color-annotations="false"] ${e}`).join(',\n');
    
    const colorRule = `
      ${selectors}
      {
          border-color: lightgrey !important;
      }
    `

    selectors = Object.keys(ColorScheme.scheme['entities']).map(e=>
      `div#annotator-root[display-annotations="true"] ${e}::before`).join(',\n');
    
    const displayRule = `
      ${selectors}
      {
          content:"";
          position: absolute;
          font-size: 0.9em;
          padding-top:1.45em;
          color:grey;
          font-family: "Font Awesome 5 Free";
          font-weight: 900;
      }
    `

    selectors = Object.keys(ColorScheme.scheme['entities']).map(e=>
      `div#annotator-root[display-annotations="false"] ${e}`).join(',\n');
    
    const hideRule = `
      ${selectors}
      {
          border-color: white !important;
      }
    `

    selectors = Object.keys(ColorScheme.scheme['entities']).join(',');
    
    const tagRule = `
      ${selectors}
      {
          min-height: 4px;
          margin: 2px 0;
          border-bottom: solid 2px white;
          cursor: default;
          background-color: white;
      }
    `

    const borderRules = Object
      .entries(ColorScheme.scheme['entities'])
      .map(e=>`${e[0]}{ border-color: ${e[1].color};}`)
      .join('\n');

    const entityFillRules = Object
      .entries(ColorScheme.scheme['entities'])
      .map(e=>`.bg-${e[0]}{ background-color: ${e[1].color};}`)
      .join('\n');

    const entityIconRules = Object
      .entries(ColorScheme.scheme['entities'])
      .map(e=>`div#annotator-root[display-annotations="true"] ${e[0]}::before{ content: "${e[1].icon}";}`)
      .join('\n');

    const entityIconColorRules = Object
      .entries(ColorScheme.scheme['entities'])
      .map(e=>`div#annotator-root[color-annotations="true"] ${e[0]}::before{ color: ${e[1].color};}`)
      .join('\n');

    return [
      colorRule,
      displayRule,
      hideRule,
      tagRule,
      borderRules,
      entityFillRules,
      entityIconRules,
      entityIconColorRules,
    ].join('\n');
  }

  function _createContentStyles(){
    const selectors = Object.keys(ColorScheme.scheme['entities']).map(e=>
      `div#annotator-root[color-annotations="false"] ${e}`).join(',\n');
    
    const rule = `
      ${selectors}
      {
          border-color: lightgrey !important;
      }
    `

    return rule;
  }

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default UISetup;