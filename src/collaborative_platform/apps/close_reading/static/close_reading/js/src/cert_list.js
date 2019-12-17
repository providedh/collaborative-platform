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

let CertaintyList = function(args){
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

		obj.subscribe('document/render', _handleDocumentRender);
    obj.subscribe('annotation/mouseenter', _handleAnnotationHover);
    obj.subscribe('annotation/mouseleave', _toggleCardHighliht);

		self = obj;
		return obj;
	}

	function _createCard(data, nested=false){
		const card_text = `<div class="card w-100 card_${data.html_target}" id="card_${data.html_target}_${data.count}">
                <div class="card-header">
                  <div class="d-flex justify-content-between">
                    <div>
                        <h5 class="card-title d-inline text-dark">Id :</h5>
                        <i class="text-muted"> ${data.id}</i>
                    </div>
                      <div>
                        <h5 class="card-title d-inline text-dark">Target :</h5>
                        <i class="text-muted target_id"> ${data.target}</i>
                      </div>
                    </div>
                    <div class="row d-flex px-3 justify-content-between">
                    <div class="text-muted">
                        By: <i>${data.author}</i>
                    </div>
                      <div>
                        <i class="text-muted">(person)</i>
                      </div>
                    </div>
                </div>
                <div class="card-body">
                  <ul class="list-group list-group-flush">
                  <li class="list-group-item">
                    <div class="row">
                      <div class="col-5 text-info">Original value</div>
                      <div class="col-7"><i>${data.original}</i></div>
                    </div>
                  </li>
                  <li class="list-group-item">
                    <div class="row">
                      <div class="col-5 text-info">Proposed value</div>
                      <div class="col-7"><i>${data.asserted}</i></div>
                    </div>
                  </li>
                  <li class="list-group-item">
                    <div class="row">
                      <div class="col-5 text-info">Certainty</div>
                      <div class="col-7"><i>${data.certainty}</i></div>
                    </div>
                  </li>
                  <li class="list-group-item">
                    <div class="row">
                      <div class="col-5 text-info">Uncertainty type</div>
                      <div class="col-7"><i>${data.type}</i></div>
                    </div>
                  </li>
                  <li class="list-group-item">
                    <div class="row">
                      <div class="col-5 text-info">Attribute</div>
                      <div class="col-7"><i>${data.attribute}</i></div>
                    </div>
                  </li>
                  <li class="list-group-item">
                    <div class="row">
                      <div class="col-5 text-info">Comments</div>
                      <div class="col-12">${data.desc}</p>
                    </div>
                  </li>
                </ul>
                  <a href="#${data.html_target}" class="card-link">Scroll to position</a>
                  <a href="#" class="card-link add-side-annotation" annotation-target=${data.target}>Add annotation</a>
                </div>
              </div>
		`

		return $.parseHTML(card_text)[0];
	}

	function _handleAddAnnotation(e){
		if(document.getElementById('toggle-panel').classList.contains('collapsed'))
			document.getElementById('toggle-panel').click();

		const target = e.target.attributes['annotation-target'].value.split('#')[1];

		const args = {
			selection: {
				text: target,
				abs_positions: null,
				by_id: true,
				target: target
			}
		}

		self.publish('sidepanel/selection', args);
	}

	function _handleDocumentRender(args){
		document.getElementById('certaintyList').innerHTML = '';

    const getAttribute = (json, attr)=>json.hasOwnProperty(attr)?json[attr].value:'';

    const seen = {};
    const annotations = [];
		Array.from(args.document.getElementsByTagName('teiHeader')[0].getElementsByTagName('certainty'), a=>a)
            .forEach(annotation=>annotation.attributes['target'].value.trim().split(" ")
            .forEach(target=>annotations.push([annotation, target])));

    annotations.sort((a,b)=>a[1]>b[1]?1:-1).forEach(pair=>{
      const annotation = pair[0],
        target = pair[1];

      const node = document.getElementById(args.XML_EXTRA_CHAR_SPACER+target.slice(1));

      if(! seen.hasOwnProperty(target)){
        seen[target] = 1;
      }else{
        seen[target] += 1;
      }

      const data = {
      	id: '98',//annotation.attributes['id'].value,
        count: seen[target],
      	target: getAttribute(annotation.attributes, 'target'),
      	html_target: args.XML_EXTRA_CHAR_SPACER+target.slice(1),
      	author: getAttribute(annotation.attributes, 'resp'),
      	original: '',
      	asserted: getAttribute(annotation.attributes, 'assertedValue'),
      	certainty: getAttribute(annotation.attributes, 'cert'),
      	type: getAttribute(annotation.attributes, 'category'),
      	attribute: '',
      	desc: getAttribute(annotation.attributes, 'desc'),
      }
      if(node != null){   
          
      }
      const card = _createCard(data);
      card.target = getAttribute(annotation.attributes, 'target');
      document.getElementById('certaintyList').appendChild(card);
    });

    Array.from(document.getElementsByClassName('add-side-annotation'))
		  .map(e=>e.addEventListener('click', event=>_handleAddAnnotation(event)));
	}

  function _handleAnnotationHover(args){
    _toggleCardHighliht(args);

    const card_target_id = 'card_' + args.target.id + '_1',
      card_target_node = document.getElementById(card_target_id);
    
    document.getElementById('certaintyList').scrollTop = card_target_node.offsetTop - 5;
  }

  function _toggleCardHighliht(args){
    const card_target_class = 'card_' + args.target.id,
      card_target_nodes = document.getElementsByClassName(card_target_class);
    
    Array.from(card_target_nodes).forEach(card_target_node=>{
      card_target_node.classList.toggle('hovered');
      
      card_target_node
        .getElementsByClassName('target_id')[0].classList.toggle('hovered');
    });
  }

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default CertaintyList;