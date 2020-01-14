import React from 'react';
import { ParentSize } from '@vx/responsive';

import styles from './style.module.css';

import DashboardControlPanel from '../DashboardControlPanel';
import ViewDetailsPanel from '../ViewDetailsPanel';
import Workspace from '../Workspace';
import Help from '../Help';
import AjaxCalls from '../../../helpers/ajax.js';

export default class Dashboard extends React.Component {
    constructor(props){
        super(props);

        this.dashboardConfig = this.props.hasOwnProperty('savedConf')?
            this.props.savedConf:{
            views:[],
            layout:[],
            authors:[],
            version: '',
        };

        this.state = {
            views: this.dashboardConfig.views,
            focusedView: -1,
            lastChangesSaved: true,
        };

        this.ajax = AjaxCalls();

        this.updateDashboardConfig = this.updateDashboardConfig.bind(this);
        this.openDetails = this.openDetails.bind(this);
        this.closeDetails = this.closeDetails.bind(this);
        this.addView = this.addView.bind(this);
        this.updateView = this.updateView.bind(this);
        this.removeView = this.removeView.bind(this);
        this.save = this.save.bind(this);
        this.setAuthors = this.setAuthors.bind(this);
        this.setVersion = this.setVersion.bind(this);
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
        this.ajax.updateDashboard(window.project, window.dashboard, data).then(()=>{
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

    setVersion(versions){
        this.setState({versions});
    }

    openDetails(viewIndex){
        this.setState({focusedView: viewIndex});
    }

    closeDetails(){
        this.setState({focusedView: -1});
    }

    render(){
        return (
            <ParentSize>
                {parent =>
                    <div className={"container-fluid " + styles.dashboard } style={{height: parent.height, width: parent.width}}>
                        <div className={"row " + styles.heightInherit}>
                            <div className={`col ${styles.heightInherit} ${styles.leftContainer}`}>
                                <div className="row justify-content-end align-items-baseline pr-3">
                                    <button onClick={this.save}
                                        type="button" 
                                        className={`btn ${this.state.lastChangesSaved===true?"btn-outline-success":"btn-primary"} h-75`}
                                        disabled={this.state.lastChangesSaved===true}>
                                        {this.state.lastChangesSaved===true?'All changes saved':'Save last changes'}
                                    </button>
                                </div>
                                <Help />
                                <Workspace 
                                    liftState={this.updateDashboardConfig}
                                    defLayout={this.dashboardConfig.layout}
                                    views={this.state.views} 
                                    focused={this.state.focusedView} 
                                    onClose={this.removeView}
                                    onFocus={this.openDetails}/>
                            </div>
                            <div className={"col-3 px-0 " + styles.heightInherit}>
                                <DashboardControlPanel 
                                    addView={this.addView} 
                                    authors={this.state.authors} 
                                    version={this.state.version} 
                                    setAuthors={this.setAuthors} 
                                    setVersion={this.setVersion}
                                    display={this.state.focusedView == -1}/>
                                {this.state.focusedView != -1 &&
                                    <ViewDetailsPanel 
                                        view={this.state.views[this.state.focusedView]} 
                                        display={true} 
                                        updateView={newConfig => this.updateView(this.state.focusedView, newConfig)}
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
