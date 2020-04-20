import React from 'react';
import { ParentSize } from '@vx/responsive';

import styles from './style.module.css';

import Status from './Status';
import DashboardControlPanel from '../DashboardControlPanel';
import ViewDetailsPanel from '../ViewDetailsPanel';
import Workspace from '../Workspace';
import Help from '../Help';
import AjaxCalls from '../../../helpers/ajax.js';
import {WithAppContext} from 'app_context';

export default (props)=>(
    <WithAppContext>
        <Dashboard {...props}/>
    </WithAppContext>
);

class Dashboard extends React.Component {
    constructor(props){
        super(props);

        this.dashboardConfig = props.savedConf!=null?
            this.props.savedConf:{
            views:[],
            layout:[],
            authors:[],
            currentVersion: props.context.projectVersions[0],
            fullscreen: false
        };

        this.state = Object.assign({},{
            focusedView: -1,
            lastChangesSaved: true,
        }, this.dashboardConfig);

        this.ajax = AjaxCalls();

        if(props.savedConf==null){ // Ensure the initial configuration is saved for fresh new dashboards
            const data = JSON.stringify(Object.assign(this.dashboardConfig, {lastChangesSaved: true}));
            this.ajax.updateDashboard({project:window.project, dashboard:window.dashboard}, {}, data)
                .then(()=>console.info('Initial state saved.'));
        }

        this.updateDashboardConfig = this.updateDashboardConfig.bind(this);
        this.handleViewFocus = this.handleViewFocus.bind(this);
        this.closeDetails = this.closeDetails.bind(this);
        this.addView = this.addView.bind(this);
        this.updateView = this.updateView.bind(this);
        this.removeView = this.removeView.bind(this);
        this.save = this.save.bind(this);
        this.setAuthors = this.setAuthors.bind(this);
        this.setVersion = this.setVersion.bind(this);
        this.toggleFullscreen = this.toggleFullscreen.bind(this);
        this.enterFullscreen = this.enterFullscreen.bind(this);
        this.exitFullscreen = this.exitFullscreen.bind(this);
        this.handleViewDetailsChange = this.handleViewDetailsChange.bind(this);
    }

    updateDashboardConfig(config) {
        this.dashboardConfig = Object.assign(this.dashboardConfig, config);
        this.setState({lastChangesSaved: false});
    }

    removeView(viewIndex){
        this.setState(prevState=>{
            prevState.views.splice(viewIndex, 1)
            prevState.focusedView = prevState.focusedView == viewIndex?-1:prevState.focusedView

            this.dashboardConfig.views = prevState.views
            prevState.lastChangesSaved = false
            return prevState
        })
    }

    updateView(viewIndex, newConfig){
        this.setState(prevState=>{
            prevState.views[viewIndex].config = newConfig

            this.dashboardConfig.views = prevState.views
            prevState.lastChangesSaved = false
            return prevState
        })
    }

    save() {
        const data = JSON.stringify(Object.assign(this.dashboardConfig, {lastChangesSaved: true}));
        this.ajax.updateDashboard({project:window.project, dashboard:window.dashboard}, {}, data).then(()=>{
            this.setState({lastChangesSaved: true});
            console.info('Dashboard saved.')
        });
    }

    addView(newView){
        this.setState(prevState => {
            const prevId = prevState.views.length==0?"0":prevState.views[prevState.views.length-1].id,
                id = String((+prevId) + 1),
                newViews = [...prevState.views, Object.assign(newView, {id})];
            prevState.views = newViews

            this.dashboardConfig.views = prevState.views
            prevState.lastChangesSaved = false
            return prevState
        })
    }

    setAuthors(authors){
        this.setState({authors});
    }

    setVersion(version){
        this.setState(prevState => {
            const newState = Object.assign({},
                prevState,
                {currentVersion: version, lastChangesSaved: false}
            );
            this.dashboardConfig.currentVersion = version;
            
            return newState;
        })
    }

    enterFullscreen(){
        this.setState(prev=>{
            if(prev.fullscreen === true)
                return prev;

            this.dashboardConfig.fullscreen = true;
            return Object.assign({},prev,{fullscreen:true, lastChangesSaved:false});
        });
    }

    exitFullscreen(){
        this.setState(prev=>{
            if(prev.fullscreen === exit)
                return prev;

            this.dashboardConfig.fullscreen = false;
            return Object.assign({},prev,{fullscreen:false, lastChangesSaved:false});
        });
    }

    toggleFullscreen(){
        this.setState(prev=>{
            const fullscreen = !prev.fullscreen;
            this.dashboardConfig.fullscreen = fullscreen;
            return Object.assign({},prev,{fullscreen, lastChangesSaved:false});
        });
    }

    handleViewFocus(viewIndex){
        if(this.state.focusedView == viewIndex){
            this.closeDetails(viewIndex);
        } else {
            this.openDetails(viewIndex);
        }       
    }

    openDetails(viewIndex){
        this.setState(prev=>{
            if(prev.fullscreen === true){
                this.dashboardConfig.fullscreen = false;
                return Object.assign({},prev,{
                    focusedView: viewIndex,
                    fullscreen:false,
                    lastChangesSaved:false
                });
            }else{
                return Object.assign({},prev,{focusedView: viewIndex});
            }
        });
    }

    closeDetails(){
        this.setState({focusedView: -1});
    }

    toggleHelp(){
        document.getElementById('help').classList.toggle('hidden');
    }

    handleViewDetailsChange(newConfig){
        this.updateView(this.state.focusedView, newConfig);
    }

    render(){
        return (
            <ParentSize>
                {parent =>
                    <div className={"container-fluid " + styles.dashboard } style={{height: parent.height, width: parent.width}}>
                        <div className={"row " + styles.heightInherit}>
                            <div className={`col ${styles.heightInherit} ${styles.leftContainer}`}>
                                <div className="row justify-content-end align-items-baseline">
                                    <Status />
                                    <button onClick={this.toggleHelp}
                                        type="button" 
                                        className="btn btn-primary h-75 mr-3">
                                        Help
                                    </button>
                                    <button onClick={this.save}
                                        type="button" 
                                        className={`btn ${this.state.lastChangesSaved===true?"btn-outline-success":"btn-primary"} h-75`}
                                        disabled={this.state.lastChangesSaved===true}>
                                        {this.state.lastChangesSaved===true?'All changes saved':'Save last changes'}
                                    </button>
                                    <button className={styles.toggleFullScreen + ' ml-3'}
                                        onClick={this.toggleFullscreen}>
                                        {this.state.fullscreen?'<< ':''}
                                        <span>{this.state.fullscreen?'Show':'Hide'} side panel</span>
                                        {this.state.fullscreen?'':' >>'}
                                    </button>
                                </div>
                                <Help />
                                <Workspace 
                                    liftState={this.updateDashboardConfig}
                                    defLayout={this.dashboardConfig.layout}
                                    views={this.state.views} 
                                    focused={this.state.focusedView} 
                                    onClose={this.removeView}
                                    onFocus={this.handleViewFocus}/>
                            </div>
                            <div className={"col-3 px-0 " + styles.heightInherit + (this.state.fullscreen?' d-none':'')}>
                                <DashboardControlPanel 
                                    addView={this.addView} 
                                    currentVersion={this.state.currentVersion} 
                                    authors={this.state.authors}
                                    setAuthors={this.setAuthors} 
                                    setVersion={this.setVersion}
                                    display={this.state.focusedView == -1}/>
                                {this.state.focusedView != -1 &&
                                    <ViewDetailsPanel 
                                        view={this.state.views[this.state.focusedView]} 
                                        display={true} 
                                        updateView={this.handleViewDetailsChange}
                                        close={this.closeDetails}/>
                                }
                            </div>
                        </div>
                    </div>
                }
            </ParentSize>
        );
    }
}
