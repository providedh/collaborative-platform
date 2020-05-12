import React from 'react';

import EntityInfo from './entityInfo';
import AttributeList from './attributeList';

export default ({data})=>[
	<EntityInfo key="ei" data={data}/>, 
	<AttributeList key="al" data={data}/>,
	];