import {useEffect} from 'react';
import * as d3 from 'd3';

import Sunburst from './sunburst';

export default function useRender(width, height, data, numLevels, levels, containerRef, callback){
    useEffect(()=>{
			const sunburst = Sunburst();
			sunburst.setEventCallback(callback);
			sunburst.render(data, numLevels, levels, containerRef.current);
        }, // Render 
        [width, height, data, numLevels, levels, containerRef]); // Conditions*/
}