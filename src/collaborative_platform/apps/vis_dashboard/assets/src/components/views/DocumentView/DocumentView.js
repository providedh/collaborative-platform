import React, { useEffect, useState, useRef } from "react";
import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';

import {AjaxCalls} from '../../../helpers';
import {DataClient} from '../../../data';

const ajax = AjaxCalls();

function useData(dataClient, syncWithViews, documentId){
	const dummyDocument = {getElementsByTagName: ()=>[{innerHTML: ''}]},
		[contents, setContents] = useState(dummyDocument);

	useEffect(()=>{
		if(syncWithViews === true){
			dataClient.unsubscribe('document');
            dataClient.subscribe('document', ({contents})=>{
                setContents(contents);
            });
		}else{
			dataClient.unsubscribe('document');
            ajax.getFile({project:window.project, file:documentId},{},null).then(response=>{
            	if(response.success === true)
            		setContents(response.content)
            });
		}

	}, [syncWithViews, documentId]);

	return contents;
}

function DocumentView({layout, syncWithViews, documentId}) {
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];
	const viewRef = useRef();

	const [dataClient, _] = useState(DataClient());
	const contents = useData(dataClient, syncWithViews, documentId);
	useEffect(()=>{viewRef.current.innerHTML = contents.getElementsByTagName('body')[0].innerHTML}, [contents]);

    return(
        <div className={styles.documentView}>
        	<div className="bg-white d-flex justify-content-between justify-space-between p-2">
	        	<span>{window.documents[documentId].name}</span>
	        	<a className="btn btn-sm btn-outline-primary" 
	        	   target="blank" 
	        	   href={`/close_reading/project/${window.project}/file/${window.documents[documentId].id}/`}>
	        	   Open in annotator
	        	</a>	
        	</div>
        	<div ref={viewRef} className={styles.documentContainer}>
        	</div>
        </div>
    )
}

DocumentView.prototype.description = "Encode frequencies using horizontal or vertical bars."

DocumentView.prototype.getConfigOptions = getConfig;

export default DocumentView;
