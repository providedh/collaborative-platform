import {useEffect} from 'react';
import * as d3 from 'd3';

import Sunburst from './sunburst';

export default function useRender(width, height, data, count, levels, containerRef, callback){
	const levelKeys = Object.entries(levels).sort((x, y)=>x[0] - y[0]).map(x=>x[1]);
	const sunburst = Sunburst();
	
    useEffect(()=>{
		if(data != null && data != undefined && count > 0){
			sunburst.setEventCallback(callback);
			sunburst.render(data, count, levels, containerRef.current);
		}
    }, // Render 
    [width, height, data, levelKeys.join('_'), containerRef]); // Conditions*/
}