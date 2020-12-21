import React from "react";
import { render } from "react-dom";
import App from "./components/app";


const appConfig = window.djangoAppConfig;
delete window.djangoAppConfig;

render(<App appConfig={appConfig}/>, document.getElementById('react-root'));