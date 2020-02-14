import React from 'react';

import icons from './font_awesome_icon_relation.js';

class IconPicker extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      search: '',
      icon: '',
      available: [],
    };
  }
  
  handleIconFilter(searchValue){
    const newState = {search: searchValue};
    
    if(searchValue != ''){
      const filtered = Object.entries(icons).filter(x=>x[0].startsWith(searchValue));
      const subset = filtered.splice(0,Math.min(10, filtered.length));
      newState['available'] = subset;
    }
    
    this.setState(newState);
  }
  
  handleIconSelect(icon){
    this.setState({icon});
  }
  
  handleIconSet(){
    if(this.state.icon != '') 
      this.props.onChange(this.state.icon);
    this.hidePicker();
    this.setState({
      search: '',
      icon: '',
      available: [],
    });
  }
  
  showPicker(){
    document.getElementById(this.props.iconKey + "-icon-picker").classList.remove('d-none');
  }
  
  hidePicker(){
    this.setState({
      search: '',
      icon: '',
      available: [],
    },()=>document.getElementById(this.props.iconKey + "-icon-picker").classList.add('d-none'));
  }
  
  render(){
    return(
      <div className="icon pointer mx-2" id={this.props.iconKey} data-icon={this.props.icon} onClick={()=>this.showPicker()}>
        <div className="iconPicker card shadow bg-white d-none" id={this.props.iconKey + "-icon-picker"}>
          <div className="card-body">
            <form>
              <div className="form-group">
                <label htmlFor={this.props.iconKey+"-search"}>Search field</label>
                <input className="form-control" 
                  id={this.props.iconKey+"-search"} 
                  onChange={e=>this.handleIconFilter(e.target.value)}
                  placeholder="Search an icon by name" />
              </div>
              <div className="form-group">
                <label htmlFor={this.props.iconKey+"-select"}>
                  {this.state.available.length} Filtered icons
                  {this.state.icon != ''?<span>(<div className="icon" data-icon={this.state.icon}></div> selected)</span>:''}:
                </label>
                <div className="chipContainer">
                  {this.state.available.map(x=>(
                   <div className={"chip border "+(this.state.icon == x[1]?'checked':'')} key={x[0]}>
                      <div className="icon" data-icon={x[1]}></div>
                      <span className="bg-white mx-1 px-2">{x[0]}</span>
                      <span className="button" 
                            onClick={e=>this.setState({icon: x[1]})}>
                            <i className={this.state.icon != x[1]?"fas fa-check":''}></i>
                      </span>
                    </div>))}
                </div>
              </div>
              <div className="form-group d-flex justify-content-between">
                <button type="button" className="btn btn-danger text-white" onClick={()=>this.hidePicker()}>Cancel</button>
                <button type="button" className="btn btn-primary text-white" onClick={()=>this.handleIconSet()}>Set icon</button>
              </div>
            </form>
           </div>
        </div>
      </div>)
  }
}

export default IconPicker;