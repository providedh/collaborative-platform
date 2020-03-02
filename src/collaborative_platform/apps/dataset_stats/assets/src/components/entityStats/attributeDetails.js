import React from 'react';

export default ({attribute, tag})=>{
	const {
		name,
		distinct_values,
		trend_percentage,
		trend_value,
		coverage
	} = attribute;

  const shorttened = t=>t.slice(0, Math.min(t.length, 20)) + (t.length>20?'...':'');

	return(<div className="row">
        <div className="col-3">
          <h4>{name}</h4>
          <p>
            {distinct_values} distinct values <br/>
            <span title={trend_value}>
            	{trend_percentage}% with value {shorttened(trend_value + '')} <br/>
            	{coverage}% tags have it<br/>
            </span>
          </p>
        </div>
        <div className="col-auto">
          <canvas 
              id="{tag}-{name}" 
              data='{"data":[]}' 
              className="chartContainer pl-5" 
              width={400} />
        </div>
        <div className="col-3">
        	{coverage > 34?'':
	            <span className="alert alert-danger d-block" role="alert">
	              Only a third or less of the entities have this.  Analysis based on this attribute can leave information out.
	            </span>
        	}

        	{distinct_values != 1?'':
	            <span className="alert alert-danger d-block" role="alert">
	              This attribute takes only one different value. Analysis based on this attribute will not provide extra information.
	            </span>
        	}

        	{distinct_values != 2 || trend_percentage < 60?'':
	            <span className="alert alert-danger d-block" role="alert">
	              This attribute takes only two different values and one is over-representated. Analysis based on this attribute can be biased.
	            </span>
        	}

        	{distinct_values < 2 || trend_percentage < 50?'':
	            <span className="alert alert-danger d-block" role="alert">
	              This attribute has an imbalanced value distribution. Analysis based on this attribute can be biased.
	            </span>
        	}
        </div>
      </div>);
}