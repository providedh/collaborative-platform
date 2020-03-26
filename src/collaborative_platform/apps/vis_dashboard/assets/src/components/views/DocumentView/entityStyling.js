export default function(container, doc, settings){
	const docEntities = settings.entities.map(e=>doc.getElementsByTagName(e.name)),
		docEntitiesFlattened = docEntities.reduce((ac, dc)=>[...ac, ...dc], []),
		containerEntities = settings.entities.map(e=>container.getElementsByTagName(e.name)),
		containerEntitiesFlattened = containerEntities.reduce((ac, dc)=>[...ac, ...dc], []),
		containerObjectNames = [...container.getElementsByTagName('objectname')],
		id2entity = Object.fromEntries(
			containerEntitiesFlattened
				.filter(x=>x.attributes.hasOwnProperty('xml:id'))
				.map(x=>[x.attributes['xml:id'].value, x])
		),
		name2style = Object.fromEntries(
			settings.entities
				.map(e=>[e.name, e])
		);

	containerEntitiesFlattened.forEach(e=>{
		const entityName = (e.attributes.hasOwnProperty('type') &&
			  name2style.hasOwnProperty(e.attributes['type'].value))
				?e.attributes['type'].value
				:e.tagName.toLowerCase();

		e.style.setProperty('border-bottom', 'solid 4px '+name2style[entityName].color);
	})

	containerObjectNames.forEach(e=>{
		if(! e.attributes.hasOwnProperty('ref'))
			return;

		const ref = e.attributes['ref'].value.slice(1); // the ref value is preceeded with an # character
		if(! id2entity.hasOwnProperty(ref))
			return;

		const target = id2entity[ref],
			  entityName = (target.attributes.hasOwnProperty('type') &&
			  name2style.hasOwnProperty(target.attributes['type'].value))
					?target.attributes['type'].value
					:target.tagName.toLowerCase();

		e.style.setProperty('border-bottom', 'solid 4px '+name2style[entityName].color);
	})
}