import React from 'react';
import { ParentSize } from '@vx/responsive';

import * as d3 from 'd3';

import create_doc from '../data/data1.js';

import css from '../themes/theme.css';

//import PixelDoc from './views/PixelDoc/PixelDoc.js';
import Dashboard from './core/Dashboard/Dashboard';
import TabContainer from './ui/TabContainer';
import {DataService} from '../data';
window.ds = DataService()

export default class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data: [],
        }
    }

    componentDidMount(){
        const synthdata = [create_doc(), create_doc()];
        this.setState({data: synthdata});
    }

    shouldComponentUpdate(nextProps, nextState){    
        return true;        
    }

    componentDidUpdate(prevProps, prevState, snapshot){

    }

    render(){
        return <Dashboard savedConf={this.props.savedConf} data={this.state.data}/>
    }
}