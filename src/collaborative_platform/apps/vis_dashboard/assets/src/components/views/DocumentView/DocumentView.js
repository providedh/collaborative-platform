import React, { useEffect, useState, useRef } from "react";

import {AjaxCalls} from '../../../helpers';
import {DataClient} from '../../../data';

import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';
import styleEntities from './entityStyling';

const ajax = AjaxCalls();

function useData(dataClient, syncWithViews, documentId){
	const [data, setData] = useState({id: '', name: '', html: ''});

	useEffect(()=>{
		if(syncWithViews === true){
			dataClient.unsubscribe('document');
            dataClient.subscribe('document', ({id, html})=>{
            	if(id!='')
                	setData({id, html: html.getElementsByTagName('body')[0].innerHTML, doc:html, name: window.documents[id].name});
                else
                	setData({id:'', html:'<i>Hover over documents in other views to see its contents here.</i>', doc: null, name:''});
            });
		}else{
			dataClient.unsubscribe('document');
            ajax.getFile({project:window.project, file:documentId},{},null).then(response=>{
            	if(response.success === true)
            		setData({
            			id: documentId, 
            			name: window.documents[documentId].name, 
                        doc: response.content,
            			html:response.content.getElementsByTagName('body')[0].innerHTML
            		});
            });
		}

	}, [syncWithViews, documentId]);

	return data;
}

function useDocumentRendering(data, container){
	useEffect(()=>{
        if(container == undefined)
            return

        container.innerHTML = data.html;
        console.log(data)
        styleEntities(container, data.doc, window.settings)
    }, [data.id]);
}

function DocumentView({layout, syncWithViews, documentId}) {
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];
	const viewRef = useRef();

	const [dataClient, _] = useState(DataClient());
	const data = useData(dataClient, syncWithViews, documentId);
    useDocumentRendering(data, viewRef.current)

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
