import React, { useState } from 'react';

import Header from './header';

export default ({data})=>{
  const [expanded, setExpanded] = useState(false);

	return(<li className="list-group-item">
    <ul className="list-group entity rounded {expanded===true?'expanded':''}">
      <Header data={data} onClick={()=>setExpanded(!expanded)}/>
    </ul>
  </li>);
}