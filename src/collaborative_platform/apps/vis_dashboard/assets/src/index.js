import React from "react";
import { render } from "react-dom";
import App from "./components/App_test";

window.dashboardSavedConf = JSON.parse('{"views":[{"type":"Histogram","config":{"barDirection":"Horizontal","dimension":"Number of entities per document","renderOverlay":true,"overlay":"Certainty level"},"id":"1"}],"layout":[{"w":8,"h":7,"x":0,"y":0,"i":"1","minW":4,"minH":4,"moved":false,"static":false,"isDraggable":true,"isResizable":true}]}')

const dashboardConfig = window.hasOwnProperty('dashboardSavedConf')?
    window.dashboardSavedConf:{
    views:[],
    layout:[]
};

render(<App savedConf={dashboardConfig} />, document.getElementById('react-root'));