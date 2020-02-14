import React from "react";
import { render } from "react-dom";
import App from "./components/App_test";

const dashboardConfig = typeof window.hasOwnProperty('config')?
    Object.assign({views:[], layout:[], authors:[], version: '',},window.config):
    {views:[], layout:[], authors:[], version: '',};

render(<App savedConf={dashboardConfig} />, document.getElementById('react-root'));