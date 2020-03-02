import React from 'react';
export default ({data})=>{
	const {
		location, 
		attributes, 
		document_count, 
		distinct_doc_occurrences, 
		coverage
	} = data;

	return(<li className="list-group-item onExpanded bg-secondary">
        <div className="d-flex flex-row">
          <div className="d-block">
            <p>
              <b className="big">{ distinct_doc_occurrences } out of { document_count } documents have this tag</b><br/>
              <b className="big">This tag is mainly found in the { location }</b><br/>
              There is a total of { attributes.length } distinct attributes <br/>for this tag in the dataset <br/>
              <br/>
            </p>
          </div>
          <div id="chartContainer" className="d-block pl-5">
            <p>
              <b>
                { coverage > 20?'':
                <span className="alert alert-danger d-block" role="alert">
                  Too few documents ({ coverage }%) have this entity. Analysis based on this tag can leave information out.
                </span>
                }
              </b>
            </p>
          </div>
        </div>
      </li>);
}
