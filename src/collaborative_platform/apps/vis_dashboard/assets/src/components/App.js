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
            contributors: [],
            projectVersions: []
        }
    }

    componentDidMount(){
        this.fetchData();
    }

    fetchData(){
        this.fetchDocuments().then(()=>
            this.fetchContributors().then(()=>
                this.fetchSettings().then(()=>
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
                        fetching: 'contributors in the project.'
                    });
                    window.documents = Object.fromEntries(response.content.map(d=>[d.id, d]));
                    resolve();
                }
            });
        });
    }

    fetchContributors(){
        return new Promise((resolve, error)=>{
            ajax.getContributors({project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve the project contributors.'});
                }else{
                    this.setState({
                        fetched: 2, 
                        contributors: response.content, 
                        fetching: 'the project settings.'
                    });
                    window.contributors = response.content;
                    resolve();
                }
            });
        });
    }

    fetchSettings(){
        return new Promise((resolve, error)=>{
            ajax.getSettings({project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve the project settings.'});
                }else{
                    this.setState({
                        fetched: 3, 
                        settings: response.content, 
                        fetching: 'project versions.'
                    });
                    window.settings = response.content;
                    resolve();
                }
            });
        });
    }

    fetchProjectVersions(){
        function processVersions(response){
            const versions = response.content.project_versions;
            versions.forEach(x=>x.date = new Date(x.date));
            const sorted = versions.sort((x,y)=>x<y?1:-1);
            return sorted;
        }

        return new Promise((resolve, error)=>{
            ajax.getProjectVersions({project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve project versions.'});
                }else{
                    this.setState({
                        fetched: 4, 
                        projectVersions: processVersions(response), 
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
            return <Dashboard savedConf={this.props.savedConf} projectVersions={this.state.projectVersions}/>
        else
            return <LoadingApp {...this.state}/>
    }
}