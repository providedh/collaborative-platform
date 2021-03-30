import React from 'react';

import EntityInfo from './entityInfo';
import AttributeList from './attributeList';

export default ({data, docCount})=>[
	<EntityInfo key="ei" data={data} docCount={docCount}/>,
	<AttributeList key="al" data={data}/>,
	];