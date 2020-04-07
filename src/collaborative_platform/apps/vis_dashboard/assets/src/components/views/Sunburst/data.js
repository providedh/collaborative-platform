import {useEffect, useState} from "react";

export default function useData(dataClient, source, levels){
    const levelKeys = Object.entries(levels).sort((x, y)=>x[0] - y[0]).map(x=>x[1]);
    const [fetched, setFetched] = useState(null);
    const [data, setData] = useState({data:null, count:0});

    useEffect(()=>{
        dataClient.unsubscribe('entity');
        dataClient.unsubscribe('certainty');
        dataClient.unsubscribe('meta');

        dataClient.subscribe(source, d=>{
        	if(d != null){
            	const trees = {
					all: createTree(d.all, levelKeys),
					filtered: createTree(d.filtered, levelKeys)
				};
				setFetched(d);
	            setData({data:trees, count:d.all.length});
        	}
        });
    }, [source])

    useEffect(()=>{
        if(fetched != null){
        	const trees = {
				all: createTree(fetched.all, levelKeys),
				filtered: createTree(fetched.filtered, levelKeys)
			};
            setData({data:trees, count:fetched.all.length});
        }
    }, [levelKeys.join('_')])

    return data;
}

function getAttrAccessor(key){
	if(key !== 'category') return entry=>entry[key];
	else return entry=>entry[key].join(', ')
}

function createTree(data, levelKeys){
	const accessors = levelKeys.map(key=>getAttrAccessor(key));
	const tree = group(data, accessors); // hierarchy
	
	return tree;
}

function group(data, keys){
	function regroup(values, i){
		if (i >= keys.length) return values;
	    const groupsMap = new Map();
	    const keyof = keys[i++];
	    let index = -1;

	    for (const value of values) {
	      const key = keyof(value)+''; // the attribute's value
	      const group = groupsMap.get(key);

	      if (group) group.children.push(value);
	      else groupsMap.set(key, {name: group, children:[value]});
	    }

	    for (const [name, group] of groupsMap) {
	    	groupsMap.set(name, {name, children:regroup(group.children, i)});
	    }

	    const groups = [...groupsMap.values()]; //[{name, children}]
	    return groups;
	}

	return regroup(data, 0);
}