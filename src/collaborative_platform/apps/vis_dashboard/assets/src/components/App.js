import React from 'react';

import css from '../themes/theme.css';

import {AppContext} from 'app_context';
import Dashboard from './core/Dashboard/Dashboard';
import LoadingApp from './LoadingApp';
import {DataClient, DataService} from '../data';
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
            id2document: null,
            name2document: null,
            taxonomy: [],
            contributors: [],
            projectVersions: [],
            appContext: null,
            project: window.project,
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
            ajax.getFiles({project: this.state.project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve project documents.'});
                }else{
                    this.setState({
                        fetched: 1, 
                        id2document: Object.fromEntries(response.content.map(d=>[d.id, d])), 
                        name2document: Object.fromEntries(response.content.map(d=>[d.name, d])),
                        fetching: 'contributors in the project.'
                    });

                    resolve();
                }
            });
        });
    }

    fetchContributors(){
        return new Promise((resolve, error)=>{
            ajax.getContributors({project: this.state.project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve the project contributors.'});
                }else{
                    this.setState({
                        fetched: 2, 
                        contributors: response.content, 
                        fetching: 'the project settings.'
                    });
                    
                    resolve();
                }
            });
        });
    }

    fetchSettings(){
        return new Promise((resolve, error)=>{
            ajax.getSettings({project: this.state.project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve the project settings.'});
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
        function processVersions(response){
            const versions = response.content.project_versions;
            versions.forEach(x=>x.date = new Date(x.date));
            const sorted = versions.sort((x,y)=>x<y?1:-1);
            return sorted;
        }

        return new Promise((resolve, error)=>{
            ajax.getProjectVersions({project: this.state.project},{},null).then(response=>{
                if(response.success === false){
                    this.setState({error: 'Failed to retrieve project versions.'});
                }else{
                    const projectVersions = processVersions(response);
                    const appContext = {
                        project: this.state.project,
                        projectVersions: projectVersions,
                        id2document: this.state.id2document, 
                        name2document: this.state.name2document, 
                        taxonomy: this.state.taxonomy, 
                        contributors: this.state.contributors
                    };
                    this.setAppContext(appContext)
                    resolve();
                }
            });
        });
    }

    setAppContext(appContext){
        DataService.setAppContext(appContext);
        this.setState({
            appContext,
            projectVersions: appContext.projectVersions,
            fetched: 4
        });
    }

    shouldComponentUpdate(nextProps, nextState){    
        return true;        
    }

    componentDidUpdate(prevProps, prevState, snapshot){

    }

    render(){
        if(this.state.fetched == 4){
            return(
                <AppContext.Provider value={this.state.appContext}>
                    <Dashboard savedConf={this.props.savedConf}/>
                </AppContext.Provider>
            );
        }else{
            return(<LoadingApp {...this.state}/>);
        }
    }
}