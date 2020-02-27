import * as d3_ from 'd3';
const d3 = {};
Object.assign(d3, d3_)
Object.assign(d3, require('d3-svg-legend'))
d3.getEvent = () => require("d3-selection").event;

import Ajax from './ajax';

export default function Timeline(args){
	const container_id = 'timeline';
	let self = {};

	function _init(args){
		self.load = _load;
		self.ajax = Ajax();
		self._container = document.getElementById(container_id);

		self.onVersionSelect = f=>{self._onVersionSelect = f; return self};

		return self;
	}

	function _days_difference(t1, t2){
	  	const milisInDay = 8.64e7;
	  	// expected YYYY-MM-DD
	  	const get_date = t=>new Date(
		    +(t.slice(0,4)), // year
		    +(t.slice(5,7)), // month
		    +(t.slice(8,10)), // day
		    0, // hours
		    0, // minutes
		    0, // seconds
		    0); //miliseconds

		const milis1 = get_date(t1).getTime(),
		    milis2 = get_date(t2).getTime(),
		    milisDiff = Math.abs(milis2-milis1),
		    daysDiff = milisDiff / milisInDay;
	  
		return daysDiff;
	}

	function _processVersions(versions){
		versions.forEach((x, i)=>x.i=i);
		const dates = {};

		for(let i=0; i<versions.length; i++){
		 	const date = versions[i].date.slice(0, 10);
		  
		  	if(!dates.hasOwnProperty(date)){
		    	let days = 0;
		    	if(i > 0){
		      		days = _days_difference(versions[i-1].date, versions[i].date);
		      		if(days > 1){
		      		  	for(let j=i; j<versions.length; j++){
		      		    	versions[j].i = versions[j].i + 5;
		      		  	}
		      		}
		    	}
		    	dates[date] = {days, i: versions[i].i};
		  	}
		}

		return [versions, dates];
	}

	function _setupContainer(){
		const paddingStyle = window.getComputedStyle(self._container)['padding'],
			paddingPixels = +(paddingStyle.slice(0, -2));

		self._container.innerHTML = '';

		self._width = self._container.clientWidth - (paddingPixels*2);
		self._height = 150;

		self._svg = d3.select(self._container)
			.append('svg')
			.attr('viewBox', [0, 0, self._width, self._height])
			.attr('width', self._width + 'px')
			.attr('height', self._height + 'px');

		self._versionsG = self._svg.append('svg:g')
			.attr('transform', 'translate(0,0)');

		self._legendG = self._svg.append('svg:g');
	}

	function _setupScales(){
		self._xScale = d3.scaleLinear()
			.domain([0, self._versions[self._versions.length-1].i])
			.range([0, self._width]);
	}

	function _renderProjectVersions(projectVersions){
		self._fileVersionSide = 20;
		self._fileVersionPadding = 5;

		let pVersions = self._versionsG.selectAll('g.pVersion').data(self._versions);
		pVersions.exit().remove();
		pVersions.enter().append('g').attr('class', 'pVersion');

		self._pVersions = self._versionsG.selectAll('g.pVersion')
			.attr('transform', d=>`translate(${self._xScale(d.i)}, 0)`);

		let fVersions = self._pVersions.selectAll('rect.fVersion').data(d=>d.files);
		fVersions.exit().remove();
		fVersions.enter().append('svg:rect').attr('class', 'fVersion');

		self._fVersions = self._pVersions.selectAll('rect.fVersion')
			.attr('x', 0)
			.attr('y', (d,i)=>i*(self._fileVersionPadding+self._fileVersionSide))
			.attr('width', 20)
			.attr('height', 20);
	}

	function _fillByAuthor(){
		const colorScale = d3.scaleOrdinal()
			.range(d3.schemeTableau10);

		self._versionsG.selectAll('rect.fVersion')
			.attr('fill', d=>colorScale(d.author));

		const legendOrdinal = d3.legendColor()
		  .orient('horizontal')
		  .shapePadding(10)
		  .cellFilter(function(d){ return d.label !== "e" })
		  .scale(colorScale);

		self._legendG
			.attr('transform', `translate(30,${self._height - 40})`)
			.call(legendOrdinal);
	}

	function _setupZoom(){
		const extent = [[0,0], [self._width, 0]],
			scaleExtent = [1, 4],
			translateExtent = [[0,0], [self._width, 0]];

		const zoom = d3.zoom()
		    .extent(extent)
		    .scaleExtent(scaleExtent)
		    .translateExtent(translateExtent)
		    .on('zoom', () => {
		    	const event = d3.getEvent();
		      	const {k, x, y} = event.transform;
		      	self._pVersions.attr('transform', d=>`translate(${x + self._xScale(d.i) * k}, 0)`);
		    })
		  
		self._svg.call(zoom)
		self._svg.call(zoom.scaleBy, self._width/self._height)
	}

	function _setupTooltips(){
		const tooltip = d3.select(self._container)
			.append('div')
			.style('position', 'fixed')
			.style('display', 'none')
			.style('width', '18rem')
			.classed('timelineTooltip', true)
			.classed('card', true);

		const body = tooltip.append('div').attr('class', 'card-body'),
			title = body.append('h6').attr('class', 'card-title'),
			subtitle = body.append('h7').attr('class', 'card-subtitle mb-2 text-muted'),
			content = body.append('p').attr('class', 'card-text');

		self._fVersions.on('mouseenter', function(d){
			const {top, left} = d3.select(this).node().getBoundingClientRect();

			title.text(d.file);
			subtitle.text('Version '+d.version);
			content.text(`Done by ${d.author} on ${d.date.slice(0, 10)}`);

		    tooltip
		    	.style('left', left + self._fileVersionSide + self._fileVersionPadding + 'px')
		    	.style('top', top + 'px')
		    	.style('display', 'initial');
		})

		self._fVersions.on('mouseleave', ()=>tooltip.style('display', 'none'));
	}

	function _load(){
		self.ajax.getVersions(window.project_id).then(d=>{
			_setupContainer();
			[self._versions, self._days] = _processVersions(d.content.project_versions);
			_setupScales();
			_renderProjectVersions(self._versions);
			_fillByAuthor();
			_setupTooltips();
			_setupZoom();
			console.log(d.content)

			console.info('loaded');
		});
	}

	return _init(args);
};