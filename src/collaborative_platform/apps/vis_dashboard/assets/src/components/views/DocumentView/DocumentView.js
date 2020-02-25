import React, { useEffect, useState, useRef } from "react";
import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';

import {DataClient} from '../../../data';

function useOverlay(renderOverlay, dimension, overlay){
	const [overlayData, setOverlayData] = useState(dummy_overlay[overlay][dimension]);

	useEffect(()=>{
		setOverlayData(renderOverlay===true?dummy_overlay[overlay][dimension]:null)
	}, [renderOverlay, dimension, overlay])

	return overlayData;
}

function DocumentView({layout, syncWithViews, documentId}) {
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];

    const [dataClient, _] = useState(DataClient());
	//const overlay_data = useOverlay(renderOverlay, dimension, overlay);

    return(
        <div className={styles.documentView}>
        </div>
    )
}

DocumentView.prototype.description = "Encode frequencies using horizontal or vertical bars."

DocumentView.prototype.getConfigOptions = getConfig;

export default DocumentView;
