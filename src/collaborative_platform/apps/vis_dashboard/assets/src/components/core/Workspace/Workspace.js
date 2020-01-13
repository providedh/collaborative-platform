import React from 'react';
import { useState, useEffect } from 'react';
import { ParentSize } from '@vx/responsive';

import css from 'grid_style_layout';
import css_ from 'grid_style_resizable';
import GridLayout from "react-grid-layout";

import styles from './style.module.css';
import './style.css';

import VisFrame from '../VisFrame';
import Views from '../../views';

const getDefPlacement = (idx, id)=>({
    i: id, 
    x: (idx * 2)%10, 
    y: Math.trunc((idx*2)/10), 
    w:4, 
    h:4, 
    minW: 4, 
    minH: 4, 
    isDraggable:true, 
    isResizable: true
})

function useLayout(defLayout, views) {
    const [layout, setLayout] = useState(defLayout);

    useEffect(()=>{
        if(layout.length < views.length){
            const newLayout = [...layout];
            for(let i=newLayout.length; i<views.length; i++){
                newLayout.push(getDefPlacement(i, views[i].id))
            }
            setLayout(newLayout);
        }
    }, [views]);

    return [layout, setLayout];
}

function useLiftingState(layout, liftState){
    useEffect(()=>{
        if(liftState != null)
            liftState({layout})
    }, [layout])
}

export default function Workspace({focused, onFocus, onClose, defLayout=[], liftState=null, views}) {
    const [layout, setLayout] = useLayout(defLayout, views);

    useLiftingState(layout, liftState)

    const viewmap = views.map((view, i) => (
        <div key={views[i].id}>
            <VisFrame index={i} focused={focused == i} onViewClose={onClose} onViewFocus={onFocus}>
                { React.createElement(Views[view.type], {...view.config, layout: layout[i]}) }                
            </VisFrame>
        </div>
    ))

    return(
        <div className={styles.workspace}>
            <ParentSize>
                {parent => 
                    <GridLayout
                        layout={layout}
                        onLayoutChange={setLayout}
                        width={parent.width}
                        draggableCancel="input,textarea,img"
                        rowHeight={90}
                        cols={10}
                        className="layout"
                        compactType={null}>
                        {viewmap}
                    </GridLayout>
                }   
            </ParentSize>
        </div>
    )
}
