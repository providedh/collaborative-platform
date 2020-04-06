import {useEffect} from 'react';
import * as d3 from 'd3';

export default function useRender(width, height, data, numLevels, levels, containerRef){
    useEffect(()=>{
        render(width, height, data, numLevels, levels, containerRef);
        }, // Render 
        [width, height, data, numLevels, levels, containerRef]); // Conditions*/
}

function render(width, height, data, numLevels, levels, containerRef){
	console.log(width, height, data, numLevels, levels, containerRef)
}