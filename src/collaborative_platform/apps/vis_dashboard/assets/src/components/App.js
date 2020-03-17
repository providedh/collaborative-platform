import React from 'react';

import css from '../themes/theme.css';

import Dashboard from './core/Dashboard/Dashboard';
import LoadingApp from './LoadingApp';
import {DataClient} from '../data';
import {AjaxCalls} from '../helpers';
const ajax = AjaxCalls();

window.dataclient = DataClient();

export default class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data: [],
            fetching: 'project documents.',
            error: '',
            fetched: 0,
            documents: [],
            taxonomy: [],
            collaborators: [],
            projectVersions: []
        }
    }

    componentDidMount(){
        this.fetchData();
    }

    fetchData(){
        this.fetchDocuments().then(()=>
            this.fetchCollaborators().then(()=>
                this.fetchTaxonomy().then(()=>
                    this.fetchProjectVersions())));
    }

    fetchDocuments(){
        return new Promise((resolve, error)=>{
            ajax.getFiles({project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve project documents.'});
                }else{
                    this.setState({
                        fetched: 1, 
                        documents: response.content, 
                        fetching: 'collaborators in the project.'
                    });
                    resolve();
                }
            });
        });
    }

    fetchCollaborators(){
        return new Promise((resolve, error)=>{
            ajax.getCollaborators({project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve the project collaborators.'});
                }else{
                    this.setState({
                        fetched: 2, 
                        collaborators: response.content, 
                        fetching: 'the taxonomy configuration.'
                    });
                    resolve();
                }
            });
        });
    }

    fetchTaxonomy(){
        return new Promise((resolve, error)=>{
            ajax.getTaxonomy({project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve the taxonomy configuration.'});
                }else{
                    this.setState({
                        fetched: 3, 
                        taxonomy: response.content, 
                        fetching: 'project versions.'
                    });
                    resolve();
                }
            });
        });
    }

    fetchProjectVersions(){
        return new Promise((resolve, error)=>{
            ajax.getProjectVersions({project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve project versions.'});
                }else{
                    this.setState({
                        fetched: 4, 
                        projectVersions: response.content, 
                    });
                    resolve();
                }
            });
        });
    }

    shouldComponentUpdate(nextProps, nextState){    
        return true;        
    }

    componentDidUpdate(prevProps, prevState, snapshot){

    }

    render(){
        if(this.state.fetched == 4)
            return <Dashboard savedConf={this.props.savedConf}/>
        else
            return <LoadingApp {...this.state}/>
    }
}