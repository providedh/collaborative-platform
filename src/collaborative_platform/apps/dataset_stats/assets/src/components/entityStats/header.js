import React from 'react';

import AttributePreview from './attributePreview';

export default ({data, onClick})=>{
	const {name, count, attributes} = data;
	let content = "";

	if(attributes.length>0){
		content = attributes.map((attr, i)=><AttributePreview attr={attr} key={i}/>);
	}else{
		content = (<span className="attributeSummary">
          	<div className="attributeStats rounded">
            	<span></span>
            	<span className="big">There are no tags with attributes in this collection</span>
            	<span></span>
          	</div>
        </span>)
	}

	return(<li>
        <div className="entitySummary" onClick={onClick}>
          <div className="block tag">
            <b className="big"><div className="badge badge-primary badge-pill">{ count } 
              <span className="onExpanded">tags found in the dataset</span>
              </div>&lt;{ name }</b>
          </div>
          <div className="block">
            <div className="attributeList">{ content }</div>
          </div>
          <div className="block tag">
            <b className="big">&gt;&lt;/{ name }&gt;</b>
            <button type="button" className="close onExpanded" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
        </div>
      </li>);
}