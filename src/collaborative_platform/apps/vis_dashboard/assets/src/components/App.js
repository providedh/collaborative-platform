import React from 'react';
import { ParentSize } from '@vx/responsive';

import * as d3 from 'd3';

import create_doc from '../data/data1.js';

import PixelDoc from './views/PixelDoc/PixelDoc.js';

export default class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data: [],
            visComponents: {}
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
        return (
            <ParentSize>
                {parent => 
                    
                }   
            </ParentSize>
        );
    }
}
            		/*<h1>Example front end app</h1>
                    <div id='squares-container'>
                        {d3.schemePastel1.map(color=>
                            <span className='square'
                                key={color}
                                style={{backgroundColor:color, 
                                    'marginRight':'30px',
                                    display:'inline-block',
                                    width:'20px', height:'20px'}}>
                            </span>)
                        }
                    </div>*/