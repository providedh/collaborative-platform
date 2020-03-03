import React, { useEffect, useState, useRef } from "react";
import styles from './style.module.css';
import css from './style.css';
import getConfig from './config';

import {DataClient} from '../../../data';


function DocumentView({layout, syncWithViews, documentId}) {
	const [width, height] = layout!=undefined?[layout.w, layout.h]:[4,4];
	const viewRef = useRef();

    return(
        <div className={styles.documentView} ref={viewRef}>
        </div>
    )
}

DocumentView.prototype.description = "Encode frequencies using horizontal or vertical bars."

DocumentView.prototype.getConfigOptions = getConfig;

export default DocumentView;
