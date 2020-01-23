/* Module: CSSstyles
 * Utility methods for retrieving the color scheme 
 * or calculating the color for a specific annotation
 *
 * */
import defConf from './taxonomy.js';
import ColorScheme from './color.js';
import CSSstyles from './cssstyles.js';

const aScheme = {
	colorBefore: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	colorContent: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level));

		gradStops.push(`${colors[0]} 0%`);
		for(let i=1; i<colors.length; i++){
			gradStops.push(`${colors[i-1]} ${100*i/colors.length}%`);
			gradStops.push(`${colors[i]} ${100*i/colors.length}%`);
		}
		gradStops.push(`${colors[colors.length - 1]} 100%`);

		return cssModule.createLinearGradient(gradStops);
	},
	colorAfter: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	greyBefore: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	greyContent: (id, annotations, currentUser, cssModule)=>{
		return 'background-color: lightgrey;';
	},
	greyAfter: (id, annotations, currentUser, cssModule)=>{
		const numberAnnotations = document.getElementById(id)._uncertainty_count;

		return `content: "${''+numberAnnotations} \\f591";`
		    +'border: solid 2px var(--primary); border-radius: 0 0 50% 50%; color: black;'
		    +'height: 20px; text-align: center; width: 28px; vertical-align: bottom;'
		    +'display: table-cell; font-weight: bold; line-height: 1em; position: absolute;'
		    +'top: -0.65em; font-family: "Font Awesome 5 Free"; font-size: .7em; right: -2px;'
		    +'padding-bottom: 5px; background-color: white;';
	},
}

const bScheme = {
	colorBefore: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	colorContent: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level));

		gradStops.push(`${colors[0]} 0%`);
		for(let i=1; i<colors.length; i++){
			gradStops.push(`${colors[i-1]} ${100*i/colors.length}%`);
			gradStops.push(`${colors[i]} ${100*i/colors.length}%`);
		}
		gradStops.push(`${colors[colors.length - 1]} 100%`);

		return cssModule.createLinearGradient(gradStops);
	},
	colorAfter: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	greyBefore: (id, annotations, currentUser, cssModule)=>{
		const node = document.getElementById(id),
			numberAnnotations = node._uncertainty_count,
			style = window.getComputedStyle(node, '::before'),
			content = style.getPropertyValue('content');
		
		return `content: ${content.slice(0,-1)} ${''+numberAnnotations} \\f591";`;
	},
	greyContent: (id, annotations, currentUser, cssModule)=>{
		return 'background-color: lightgrey;';
	},
	greyAfter: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			color4author = (author, currentUser) => author=='#'+currentUser?'#fff0':'#ffff';

		let [,, author, xmlid] = annotations[0],
			color = color4author(author, currentUser);
		gradStops.push(`${color} 0%`);

		for(let i=1; i<annotations.length; i++){
			let [,, prevAuthor, prevxmlid] = annotations[i-1],
				prevColor = color4author(prevAuthor, currentUser);
			[,, author, xmlid] = annotations[i],
			color = color4author(author, currentUser);

			gradStops.push(`${prevColor} ${100*i/annotations.length}%`);
			gradStops.push(`${color} ${100*i/annotations.length}%`);
		}

		[,, author, xmlid] = annotations[annotations.length-1],
			color = color4author(author, currentUser);
		gradStops.push(`${color} 100%`);

		const grad = cssModule.createLinearGradient(gradStops);
		
		return("content: '';"
			+ 'width: 100%;'
		    + 'position: absolute;'
		    + 'left: 0;'
		    + 'top: 0;'
		    + 'height: 35%;'
			+ grad);
	}
}

const cScheme = {
	colorBefore: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	colorContent: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	colorAfter: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			numberAnnotations = document.getElementById(id)._uncertainty_count,
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level)),
			color4author = (color, author, currentUser) => color,
			annotationSpacer = 10,
			percIncrement = (100 - numberAnnotations*annotationSpacer)/annotations.length//author=='#'+currentUser?'#fff0':'#ffff';
			
		let curPercentage = percIncrement;
		let prevAuthor, prevXmlid, prevColor, author, xmlid;

		[,, author] = annotations[0];
		let color = color4author(colors[0], author, currentUser);
		gradStops.push(`${color} 0%`);

		for(let i=1; i<annotations.length; i++){
			[,, prevAuthor, prevXmlid] = annotations[i-1];
			prevColor = color4author(colors[i-1], prevAuthor, currentUser);
			[,, author, xmlid] = annotations[i];
			color = color4author(colors[i], author, currentUser);

			if(xmlid != prevXmlid){
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage + annotationSpacer}%`);
				gradStops.push(`${color} ${curPercentage + annotationSpacer}%`);
				curPercentage += (annotationSpacer + percIncrement);
			}else{
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`${color} ${curPercentage}%`);
				curPercentage += percIncrement;
			}
		}

		[,, author] = annotations[annotations.length-1],
			color = color4author(colors[colors.length-1], author, currentUser);
		gradStops.push(`${color} 100%`);

		const grad = cssModule.createLinearGradient(gradStops);
		
		return grad;
	},
	greyBefore: (id, annotations, currentUser, cssModule)=>{
		return 'position: initial;';
	},
	greyContent: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	greyAfter: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			numberAnnotations = document.getElementById(id)._uncertainty_count,
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level)),
			color4author = (color, author, currentUser) => 'lightgrey',
			annotationSpacer = 10,
			percIncrement = (100 - numberAnnotations*annotationSpacer)/annotations.length//author=='#'+currentUser?'#fff0':'#ffff';
			
		let curPercentage = percIncrement;
		let prevAuthor, prevXmlid, prevColor, author, xmlid;

		[,, author] = annotations[0];
		let color = color4author(colors[0], author, currentUser);
		gradStops.push(`${color} 0%`);

		for(let i=1; i<annotations.length; i++){
			[,, prevAuthor, prevXmlid] = annotations[i-1];
			prevColor = color4author(colors[i-1], prevAuthor, currentUser);
			[,, author, xmlid] = annotations[i];
			color = color4author(colors[i], author, currentUser);

			if(xmlid != prevXmlid){
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage + annotationSpacer}%`);
				gradStops.push(`${color} ${curPercentage + annotationSpacer}%`);
				curPercentage += (annotationSpacer + percIncrement);
			}else{
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`${color} ${curPercentage}%`);
				curPercentage += percIncrement;
			}
		}

		[,, author] = annotations[annotations.length-1],
			color = color4author(colors[colors.length-1], author, currentUser);
		gradStops.push(`${color} 100%`);

		const grad = cssModule.createLinearGradient(gradStops);
		
		return("content: '';"
			+ 'width: 100%;'
		    + 'position: absolute;'
		    + 'left: 0;'
		    + 'bottom: -16px;'
		    + 'height: 14px;'
			+ grad);
	}
}

const dScheme = {
	colorBefore: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	colorContent: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			numberAnnotations = document.getElementById(id)._uncertainty_count,
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level)),
			color4author = (color, author, currentUser) => color,
			annotationSpacer = 10,
			percIncrement = (100 - numberAnnotations*annotationSpacer)/annotations.length//author=='#'+currentUser?'#fff0':'#ffff';
			
		let curPercentage = percIncrement;
		let prevAuthor, prevXmlid, prevColor, author, xmlid;

		[,, author] = annotations[0];
		let color = color4author(colors[0], author, currentUser);
		gradStops.push(`${color} 0%`);

		for(let i=1; i<annotations.length; i++){
			[,, prevAuthor, prevXmlid] = annotations[i-1];
			prevColor = color4author(colors[i-1], prevAuthor, currentUser);
			[,, author, xmlid] = annotations[i];
			color = color4author(colors[i], author, currentUser);

			if(xmlid != prevXmlid){
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage + annotationSpacer}%`);
				gradStops.push(`${color} ${curPercentage + annotationSpacer}%`);
				curPercentage += (annotationSpacer + percIncrement);
			}else{
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`${color} ${curPercentage}%`);
				curPercentage += percIncrement;
			}
		}

		[,, author] = annotations[annotations.length-1],
			color = color4author(colors[colors.length-1], author, currentUser);
		gradStops.push(`${color} 100%`);

		const grad = cssModule.createLinearGradient(gradStops);
		
		return grad;
	},
	colorAfter: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	greyBefore: (id, annotations, currentUser, cssModule)=>{
		const node = document.getElementById(id),
			numberAnnotations = node._uncertainty_count,
			style = window.getComputedStyle(node, '::before'),
			content = style.getPropertyValue('content');
		
		return `content: ${content.slice(0,-1)} ${''+numberAnnotations} \\f591";`;
	},
	greyContent: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			numberAnnotations = document.getElementById(id)._uncertainty_count,
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level)),
			color4author = (color, author, currentUser) => 'lightgrey',
			annotationSpacer = 10,
			percIncrement = (100 - numberAnnotations*annotationSpacer)/annotations.length//author=='#'+currentUser?'#fff0':'#ffff';
			
		let curPercentage = percIncrement;
		let prevAuthor, prevXmlid, prevColor, author, xmlid;

		[,, author] = annotations[0];
		let color = color4author(colors[0], author, currentUser);
		gradStops.push(`${color} 0%`);

		for(let i=1; i<annotations.length; i++){
			[,, prevAuthor, prevXmlid] = annotations[i-1];
			prevColor = color4author(colors[i-1], prevAuthor, currentUser);
			[,, author, xmlid] = annotations[i];
			color = color4author(colors[i], author, currentUser);

			if(xmlid != prevXmlid){
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage + annotationSpacer}%`);
				gradStops.push(`${color} ${curPercentage + annotationSpacer}%`);
				curPercentage += (annotationSpacer + percIncrement);
			}else{
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`${color} ${curPercentage}%`);
				curPercentage += percIncrement;
			}
		}

		[,, author] = annotations[annotations.length-1],
			color = color4author(colors[colors.length-1], author, currentUser);
		gradStops.push(`${color} 100%`);

		const grad = cssModule.createLinearGradient(gradStops);
		
		return grad;
	},
	greyAfter: (id, annotations, currentUser, cssModule)=>{
		return '';
	}
}

const eScheme = {
	colorBefore: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	colorContent: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			numberAnnotations = document.getElementById(id)._uncertainty_count,
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level)),
			color4author = (color, author, currentUser) => color,
			annotationSpacer = 10,
			percIncrement = (100 - numberAnnotations*annotationSpacer)/annotations.length//author=='#'+currentUser?'#fff0':'#ffff';
			
		let curPercentage = percIncrement;
		let prevAuthor, prevXmlid, prevColor, author, xmlid;

		[,, author] = annotations[0];
		let color = color4author(colors[0], author, currentUser);
		gradStops.push(`${color} 0%`);

		for(let i=1; i<annotations.length; i++){
			[,, prevAuthor, prevXmlid] = annotations[i-1];
			prevColor = color4author(colors[i-1], prevAuthor, currentUser);
			[,, author, xmlid] = annotations[i];
			color = color4author(colors[i], author, currentUser);

			if(xmlid != prevXmlid){
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage + annotationSpacer}%`);
				gradStops.push(`${color} ${curPercentage + annotationSpacer}%`);
				curPercentage += (annotationSpacer + percIncrement);
			}else{
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`${color} ${curPercentage}%`);
				curPercentage += percIncrement;
			}
		}

		[,, author] = annotations[annotations.length-1],
			color = color4author(colors[colors.length-1], author, currentUser);
		gradStops.push(`${color} 100%`);

		const grad = cssModule.createLinearGradient(gradStops);
		
		return grad;
	},
	colorAfter: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	greyBefore: (id, annotations, currentUser, cssModule)=>{
		const node = document.getElementById(id),
			numberAnnotations = node._uncertainty_count,
			style = window.getComputedStyle(node, '::before'),
			content = style.getPropertyValue('content');
		
		return `content: ${content.slice(0,-1)} ${''+numberAnnotations} \\f591";`;
	},
	greyContent: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			numberAnnotations = document.getElementById(id)._uncertainty_count,
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level)),
			color4author = (color, author, currentUser) => 'lightgrey',
			annotationSpacer = 10,
			percIncrement = (100 - numberAnnotations*annotationSpacer)/annotations.length//author=='#'+currentUser?'#fff0':'#ffff';
			
		let curPercentage = percIncrement;
		let prevAuthor, prevXmlid, prevColor, author, xmlid;

		[,, author] = annotations[0];
		let color = color4author(colors[0], author, currentUser);
		gradStops.push(`${color} 0%`);

		for(let i=1; i<annotations.length; i++){
			[,, prevAuthor, prevXmlid] = annotations[i-1];
			prevColor = color4author(colors[i-1], prevAuthor, currentUser);
			[,, author, xmlid] = annotations[i];
			color = color4author(colors[i], author, currentUser);

			if(xmlid != prevXmlid){
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage + annotationSpacer}%`);
				gradStops.push(`${color} ${curPercentage + annotationSpacer}%`);
				curPercentage += (annotationSpacer + percIncrement);
			}else{
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`${color} ${curPercentage}%`);
				curPercentage += percIncrement;
			}
		}

		[,, author] = annotations[annotations.length-1],
			color = color4author(colors[colors.length-1], author, currentUser);
		gradStops.push(`${color} 100%`);

		const grad = cssModule.createLinearGradient(gradStops);
		
		return grad;
	},
	greyAfter: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			numberAnnotations = document.getElementById(id)._uncertainty_count,
			colors = annotations.map(([source, level, author, xmlid])=>ColorScheme.calculate(source, level)),
			color4author = (color, author, currentUser) => author=='#'+currentUser?'#fff0':'#ffff',
			annotationSpacer = 10,
			percIncrement = (100 - numberAnnotations*annotationSpacer)/annotations.length//author=='#'+currentUser?'#fff0':'#ffff';
			
		let curPercentage = percIncrement;
		let prevAuthor, prevXmlid, prevColor, author, xmlid;

		[,, author] = annotations[0];
		let color = color4author(colors[0], author, currentUser);
		gradStops.push(`${color} 0%`);

		for(let i=1; i<annotations.length; i++){
			[,, prevAuthor, prevXmlid] = annotations[i-1];
			prevColor = color4author(colors[i-1], prevAuthor, currentUser);
			[,, author, xmlid] = annotations[i];
			color = color4author(colors[i], author, currentUser);

			if(xmlid != prevXmlid){
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage}%`);
				gradStops.push(`#fff ${curPercentage + annotationSpacer}%`);
				gradStops.push(`${color} ${curPercentage + annotationSpacer}%`);
				curPercentage += (annotationSpacer + percIncrement);
			}else{
				gradStops.push(`${prevColor} ${curPercentage}%`);
				gradStops.push(`${color} ${curPercentage}%`);
				curPercentage += percIncrement;
			}
		}

		[,, author] = annotations[annotations.length-1],
			color = color4author(colors[colors.length-1], author, currentUser);
		gradStops.push(`${color} 100%`);

		const grad = cssModule.createLinearGradient(gradStops);
		
		return("content: '';"
			+ 'width: 100%;'
		    + 'position: absolute;'
		    + 'left: 0;'
		    + 'top: 0;'
		    + 'height: 35%;'
			+ grad);
	}
}

const fScheme = {
	colorBefore: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	colorContent: (id, annotations, currentUser, cssModule)=>{
		const gradStops = [],
			colors = annotations.map(([source, level, author])=>ColorScheme.calculate(source, level));

		gradStops.push(`${colors[0]} 0%`);
		for(let i=1; i<colors.length; i++){
			gradStops.push(`${colors[i-1]} ${100*i/colors.length}%`);
			gradStops.push(`${colors[i]} ${100*i/colors.length}%`);
		}
		gradStops.push(`${colors[colors.length - 1]} 100%`);

		return cssModule.createLinearGradient(gradStops);
	},
	colorAfter: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	greyBefore: (id, annotations, currentUser, cssModule)=>{
		return '';
	},
	greyContent: (id, annotations, currentUser, cssModule)=>{
		return 'background-color: lightgrey;';
	},
	greyAfter: (id, annotations, currentUser, cssModule)=>{
		return `content: "${''+annotations.length} \\f591";`
		    +'border: solid 2px var(--primary); border-radius: 0 0 50% 50%; color: black;'
		    +'height: 20px; text-align: center; width: 28px; vertical-align: bottom;'
		    +'display: table-cell; font-weight: bold; line-height: 1em; position: relative;'
		    +'top: -0.6em; font-family: "Font Awesome 5 Free"; font-size: .7em; left: 2px;'
		    +'padding-bottom: 5px; background-color: white;';
	},

}

export default function CertaintyStyler(args){
	let self = null,
		currentUser = '';
	const styleContainerId = 'certainty';
	const css = CSSstyles({styleContainerId});
	const schemes = {
		aScheme,
		bScheme,
		cScheme,
		dScheme,
		eScheme,
		fScheme
	}

	function _init(args){
		if(!args.hasOwnProperty('currentUser'))
			return null;

		currentUser = args['currentUser']
		const obj = {applyScheme: _applyScheme};
	
		self = obj;
		return obj;
	}

	function _styleEntity(entity, scheme){
		const [id, annotations] = entity,
			colorSelector = `div#annotator-root[display-uncertainty=true][color-uncertainty=true] #${id}`,
			greySelector = `div#annotator-root[display-uncertainty=true] #${id}`;

		css.addBeforeRule(colorSelector, scheme.colorBefore(id, annotations, currentUser, css));
		css.addRule(colorSelector, scheme.colorContent(id, annotations, currentUser, css));
		css.addAfterRule(colorSelector, scheme.colorAfter(id, annotations, currentUser, css));

		css.addBeforeRule(greySelector, scheme.greyBefore(id, annotations, currentUser, css));
		css.addRule(greySelector, scheme.greyContent(id, annotations, currentUser, css));
		css.addAfterRule(greySelector, scheme.greyAfter(id, annotations, currentUser, css));
	}

	function _styleEntities(entities, scheme){
		css.resetStyles();
		entities.forEach(e=>_styleEntity(e, scheme));
	}

	function _applyScheme(entities, schemeName){
		if(schemes.hasOwnProperty(schemeName)){
			_styleEntities(entities, schemes[schemeName]);
		}
	}

	return _init(args);
}