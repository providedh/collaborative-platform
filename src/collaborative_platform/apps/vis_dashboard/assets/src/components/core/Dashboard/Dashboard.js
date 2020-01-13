import React from 'react';
import { ParentSize } from '@vx/responsive';

import styles from './style.module.css';

import DashboardControlPanel from '../DashboardControlPanel';
import ViewDetailsPanel from '../ViewDetailsPanel';
import Workspace from '../Workspace';

export default class Dashboard extends React.Component {
    constructor(props){
        super(props);

        this.dashboardConfig = this.props.hasOwnProperty('savedConf')?
            this.props.savedConf:{
            views:[],
            layout:[]
        };

        this.state = {
            views: this.dashboardConfig.views,
            focusedView: -1,
            lastChangesSaved: true,
        };

        this.updateDashboardConfig = this.updateDashboardConfig.bind(this);
        this.openDetails = this.openDetails.bind(this);
        this.closeDetails = this.closeDetails.bind(this);
        this.addView = this.addView.bind(this);
        this.updateView = this.updateView.bind(this);
        this.removeView = this.removeView.bind(this);
        this.save = this.save.bind(this);
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
        console.log(JSON.stringify(this.dashboardConfig))
        this.setState({lastChangesSaved: true});
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
                                        {this.state.lastChangesSaved?'All changes saved':'Save last changes'}
                                    </button>
                                </div>
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
