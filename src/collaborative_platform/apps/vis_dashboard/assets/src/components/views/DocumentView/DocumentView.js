import React, { useEffect, useState, useRef } from "react";
import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';

import {AjaxCalls} from '../../../helpers';
import {DataClient} from '../../../data';

const ajax = AjaxCalls();

function useData(dataClient, syncWithViews, documentId){
	const [data, setData] = useState({id: '', name: '', html: ''});

	useEffect(()=>{
		if(syncWithViews === true){
			dataClient.unsubscribe('document');
            dataClient.subscribe('document', ({id, html})=>{
            	if(id!='')
                	setData({id, html: html.getElementsByTagName('body')[0].innerHTML, name: window.documents[id].name});
                else
                	setData({id:'', html:'<i>Hover over documents in other views to see its contents here.</i>', name:''});
            });
		}else{
			dataClient.unsubscribe('document');
            ajax.getFile({project:window.project, file:documentId},{},null).then(response=>{
            	if(response.success === true)
            		setData({
            			id: documentId, 
            			name: window.documents[documentId].name, 
            			html:response.content.getElementsByTagName('body')[0].innerHTML
            		});
            });
		}

	}, [syncWithViews, documentId]);

	return data;
}

function DocumentView({layout, syncWithViews, documentId}) {
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];
	const viewRef = useRef();

	const [dataClient, _] = useState(DataClient());
	const data = useData(dataClient, syncWithViews, documentId);
	useEffect(()=>{viewRef.current.innerHTML = data.html}, [data.id]);

    return(
        <div className={styles.documentView}>
        	<div className="bg-white d-flex justify-content-between justify-space-between p-2">
	        	<span>{data.name}</span>
	        	{data.id!=''?(
		        	<a className="btn btn-sm btn-outline-primary" 
		        	   target="blank" 
		        	   href={`/close_reading/project/${window.project}/file/${data.id}/`}>
		        	   Open in annotator
		        	</a>):''}
        	</div>
        	<div ref={viewRef} className={styles.documentContainer}>
        	</div>
        </div>
    )
}

DocumentView.prototype.description = "Encode frequencies using horizontal or vertical bars."

DocumentView.prototype.getConfigOptions = getConfig;

export default DocumentView;
