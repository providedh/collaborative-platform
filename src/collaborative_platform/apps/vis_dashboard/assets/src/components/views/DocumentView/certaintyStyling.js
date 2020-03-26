export default function(container, doc, settings){
	const annotations = [...doc.getElementsByTagName('certainty')],
		targets = getTargets(annotations),
		id2annotations = Object.fromEntries(targets.map(e=>[e,[]])),
		containerEntities = [...settings.entities, {name: 'objectname'}].map(e=>container.getElementsByTagName(e.name)),
		containerEntitiesFlattened = containerEntities.reduce((ac, dc)=>[...ac, ...dc], []),
		id2entity = Object.fromEntries(
			containerEntitiesFlattened
				.filter(x=>x.attributes.hasOwnProperty('xml:id'))
				.map(x=>[x.attributes['xml:id'].value, x])
		);

	annotations.forEach(annotation=>{
		annotation.attributes['target'].value
			.split(' ')
			.map(x=>x.slice(1))
			.forEach(t=>id2annotations[t].push(annotation));
	});

	targets.forEach(target=>{
		applyStyle(id2entity[target], id2annotations[target], settings);
	});
}

function applyStyle(node ,annotations, settings){
	const categoryPrefix = 'https://providedh-test.ehum.psnc.pl/api/projects/17/taxonomy/#',
		category2style = Object.fromEntries(settings.taxonomy.map(x=>[x.name, x])),
		gradStops = [],
		numberAnnotations = annotations.length,
		annotationSpacer = 10,
		percIncrement = (100 - ((numberAnnotations-1)*annotationSpacer))/annotations.length;//author=='#'+currentUser?'#fff0':'#ffff';
		
	let curPercentage = percIncrement;

	const firstCategory = annotations[0]
		.attributes['ana'].value
		.split(' ')[0]
		.split('#')[1];

	let color = category2style[firstCategory].color,
		prevColor = color;
	gradStops.push(`${color} 0%`);

	annotations.forEach((annotation,i)=>{
		annotation.attributes['ana'].value.split(' ').forEach(category=>{
			color = category2style[category.split('#')[1]].color + 'ff';

			gradStops.push(`${prevColor} ${curPercentage}%`);
			gradStops.push(`${color} ${curPercentage}%`);
			curPercentage += percIncrement;

			prevColor = color;
		});

		if(i<=numberAnnotations-2){
			curPercentage -= percIncrement;		
			gradStops.push(`var(--light) ${curPercentage}%`);
			curPercentage += annotationSpacer;
			prevColor = 'var(--light)';
		}
	});

	gradStops.push(`${prevColor} 100%`);

	node.style.setProperty('background', `linear-gradient(to right, ${gradStops.join(', ')})`);
}

function createLinearGradient(grad_stops, orientation=0){
	const grad_stops_joined = grad_stops.join(', '), 
		grad =`
			background: -moz-linear-gradient(left, ${grad_stops_joined});
			background: -webkit-gradient(left top, ${grad_stops_joined});
			background: -webkit-linear-gradient(left, ${grad_stops_joined});
			background: -o-linear-gradient(left, ${grad_stops_joined});
			background: -ms-linear-gradient(left, ${grad_stops_joined});
			background: ;
		`;
	return grad;
}

function getTargets(annotations){
	const targets = annotations.map(a=>a.attributes['target'].value),
		splitted = targets.reduce((ac,dc)=>[...ac, ...dc.split(' ')], []),
		trimmed = splitted.map(x=>x.slice(1)),
		unique = [...(new Set(trimmed)).values()];
	return unique;
}