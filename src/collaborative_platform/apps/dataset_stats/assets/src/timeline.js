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
		const dates = {},
			timeSpanPadding = 4;

		for(let i=0; i<versions.length; i++){
		 	const date = versions[i].date.slice(0, 10);
		  
		  	if(!dates.hasOwnProperty(date)){
		    	let days = 0;
		    	if(i > 0){
		      		days = _days_difference(versions[i-1].date, versions[i].date);
		      		if(days > 1){
		      		  	for(let j=i; j<versions.length; j++){
		      		    	versions[j].i = versions[j].i + timeSpanPadding;
		      		  	}
		      		}
		    	}
		    	dates[date] = {date, days, i: versions[i].i};
		  	}
		}

		return [versions, Object.values(dates), timeSpanPadding];
	}

	function _setupContainer(){
		const paddingStyle = window.getComputedStyle(self._container)['padding'],
			paddingPixels = +(paddingStyle.slice(0, -2));

		self._container.innerHTML = `
			<svg height="10" width="10" xmlns="http://www.w3.org/2000/svg" version="1.1"> 
				<defs> 
					<pattern id="diagonal-stripe" patternUnits="userSpaceOnUse" width="10" height="10"> 
						<rect x="0" y="0" width="10" height="10" fill="white"/>
						<line x1="0" x2="10" y1="10" y2="0" id="patternLine"/>
					</pattern> 
				</defs> 
			</svg>`;

		self._width = self._container.clientWidth - (paddingPixels*2);
		self._height = 170;
		self._legendY = self._height - 40;

		self._svg = d3.select(self._container).select('svg')
			.attr('viewBox', [0, 0, self._width, self._height])
			.attr('width', self._width + 'px')
			.attr('height', self._height + 'px');

		self._legendG = self._svg.append('svg:g').attr('class', 'legendG');
		self._timeG = self._svg.append('svg:g').attr('class', 'timeG');
		self._versionsG = self._svg.append('svg:g')
			.attr('transform', 'translate(0,20)');

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

		let labels = self._pVersions.selectAll('text.projectVersionLabel').data(d=>d.files);
		labels.exit().remove();
		labels.enter().append('svg:text').attr('class', 'projectVersionLabel');

		self._fVersions = self._pVersions.selectAll('text.projectVersionLabel')
			.attr('x', 0)
			.attr('y', -5)
			.text(d=>'V.'+d.version);

		let fVersions = self._pVersions.selectAll('rect.fVersion').data(d=>d.files);
		fVersions.exit().remove();
		fVersions.enter().append('svg:rect').attr('class', 'fVersion');

		self._fVersions = self._pVersions.selectAll('rect.fVersion')
			.attr('x', 0)
			.attr('y', (d,i)=>i*(self._fileVersionPadding+self._fileVersionSide))
			.attr('width', 20)
			.attr('height', 20);
	}

	function _repositionProjectVersions({x, y, k}){
		self._pVersions.attr('transform', d=>`translate(${x + self._xScale(d.i) * k}, 0)`);
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
			.attr('transform', `translate(30,${self._legendY})`)
			.call(legendOrdinal);
	}

	function _renderTimeline(){
		const height = 60;
		self._timeG.attr('transform', `translate(0, ${self._legendY - height})`);

		let dayR = self._timeG.selectAll('rect.day').data(self._dates);
		dayR.exit().remove();
		dayR.enter().append('svg:rect').attr('class', 'day');

		dayR = self._timeG.selectAll('rect.day');
		dayR
			.attr('y', height-self._legendY)
			.attr('height', self._legendY - height + 20)
			.attr('x', d=>self._xScale(d.i))
			.attr('width', (d,i)=>{
				const nextX = (i+1 < self._dates.length)?
					self._xScale(self._dates[i+1].i):
					self._width;

				//console.log(self._xScale(d.i), nextX)
				return nextX-self._xScale(d.i);
			});

		let dateT = self._timeG.selectAll('text.date').data(self._dates);
		dateT.exit().remove();
		dateT.enter().append('svg:text').attr('class', 'date');

		dateT = self._timeG.selectAll('text.date');
		dateT
			.text(d=>d.date)
			.attr('x', d=>self._xScale(d.i))
			.attr('y', 35);

	}

	function _repositionTimeline({k, x, y}){
		self._timeG.selectAll('text.date').attr('x', d=>x + self._xScale(d.i)*k);
		self._timeG.selectAll('rect.day')
      		.attr('x', d=>x + self._xScale(d.i)*k)
      		.attr('width', (d,i)=>{
				const nextX = x + k * ((i+1 < self._dates.length)?
					self._xScale(self._dates[i+1].i):
					self._width);

      			console.log(self._xScale(d.i), nextX)

				return nextX-(x + k * self._xScale(d.i));
			});
	}

	function _renderTimeSpans(){
		const height = 60;
		self._timeG.attr('transform', `translate(0, ${self._legendY - height + 20})`);

		const timeSpans = self._dates.filter(d=>d.days > 1);

		let spanR = self._timeG.selectAll('rect.timeSpan').data(timeSpans);
		spanR.exit().remove();
		spanR.enter().append('svg:rect').attr('class', 'timeSpan');

		spanR = self._timeG.selectAll('rect.timeSpan');
		spanR
			.attr('y', height-self._legendY)
			.attr('height', self._legendY - height + 20)
			.attr('x', d=>self._xScale(d.i - self._timeSpanPadding))
			.attr('width', (d,i)=>self._xScale(self._timeSpanPadding));

		let ellapsedG = self._timeG.selectAll('g.ellapsed').data(timeSpans);
		ellapsedG.exit().remove();
		ellapsedG.enter().append('svg:g').attr('class', 'ellapsed');

		const spanText = d=>`${d.days} days`;

		ellapsedG = self._timeG.selectAll('g.ellapsed')
			.attr('transform', d=>`translate(${self._xScale(d.i - self._timeSpanPadding + 1)}, 0)`)
			.each(function(d){
				d3.select(this).append('svg:rect')
					.attr('x', 0)
					.attr('y', -35)
					.attr('width', self._xScale(self._timeSpanPadding / 2))
					.attr('height', 25)

				d3.select(this).append('svg:text')
					.attr('x', self._xScale(self._timeSpanPadding / 2)/2)
					.attr('y', -15)
					.text(spanText(d));
			})
		
		self._timeG.append('svg:line')
			.attr('x1', 0)
			.attr('x2', self._width)
			.attr('y1', 20)
			.attr('y2', 20);
	}

	function _repositionTimeSpans({k, x, y}){
		self._timeG.selectAll('rect.timeSpan')
      		.attr('x', d=>x + self._xScale(d.i - self._timeSpanPadding)*k)
      		.attr('width', (d,i)=>k * self._xScale(self._timeSpanPadding));

      	const spanText = d=>`${d.days} days`;
      	self._timeG.selectAll('g.ellapsed')
			.attr('transform', d=>`translate(${x + self._xScale(d.i - self._timeSpanPadding + 1)*k}, 0)`)
			.each(function(d){
				d3.select(this).select('rect')
					.attr('width', self._xScale(self._timeSpanPadding / 2)*k);
				d3.select(this).select('text')
					.attr('x', (self._xScale(self._timeSpanPadding / 2)*k)/2);
			});
	}

	function _setupZoom(){
		const extent = [[0,0], [self._width, 0]],
			scaleExtent = [1, 4],
			translateExtent = [[0,0], [self._width*2, 0]];

		const zoom = d3.zoom()
		    .extent(extent)
		    .scaleExtent(scaleExtent)
		    .translateExtent(translateExtent)
		    .on('zoom', () => {
		    	const event = d3.getEvent();
		      	_repositionProjectVersions(event.transform);
		      	_repositionTimeline(event.transform);
		      	_repositionTimeSpans(event.transform);
		    })
		  
		self._timeG.call(zoom)
		self._timeG.call(zoom.scaleBy, self._width/self._height)
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
			[self._versions, self._dates, self._timeSpanPadding] = _processVersions(d.content.project_versions);
			_setupScales();
			_renderTimeline();
			_renderTimeSpans();
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