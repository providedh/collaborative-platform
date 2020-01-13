import React from "react";
import { render } from "react-dom";
import App from "./components/App_test";

window.dashboardSavedConf = JSON.parse('{"views":[{"type":"PixelDoc","config":{"documentId":"#1","dimension":"entityType"},"id":"1"},{"type":"PixelDoc","config":{"documentId":"#3","dimension":"certaintyType"},"id":"2"},{"type":"Dummy","config":{"backgroundColor":"#fff","documentId":"#1","dimension":"two","tickets":["one","two"],"gender":21,"periodOfTime":20,"name":"","power":true},"id":"3"}],"layout":[{"w":4,"h":4,"x":4,"y":0,"i":"1","minW":4,"minH":4,"moved":false,"static":false,"isDraggable":true,"isResizable":true},{"w":4,"h":4,"x":0,"y":4,"i":"2","minW":4,"minH":4,"moved":false,"static":false,"isDraggable":true,"isResizable":true},{"w":4,"h":4,"x":0,"y":0,"i":"3","minW":4,"minH":4,"moved":false,"static":false,"isDraggable":true,"isResizable":true}]}')

const dashboardConfig = window.hasOwnProperty('dashboardSavedConf')?
    window.dashboardSavedConf:{
    views:[],
    layout:[]
};

render(<App savedConf={dashboardConfig} />, document.getElementById('react-root'));