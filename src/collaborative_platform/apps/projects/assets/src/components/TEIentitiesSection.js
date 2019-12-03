import React from 'react';

import IconPicker from './IconPicker.js';

class TEIentitiesSection extends React.Component {
  constructor(props){
    super(props);
    
    this.defState = {
      icon: "\uf042",
      color: '',
      name: '',
    };
    this.state = this.defState;
  }
  
  createExampleParagraphs(){
    const wordPool = "Proin in urna metus. Integer urna mauris, dapibus in lacus sed, dictum porttitor metus.".split(" ");
    const fragments = this.props.scheme.map((e,i)=>{
        const pre = Math.trunc(Math.random()*wordPool.length),
              preWordCount = 1 + Math.trunc(Math.random()*(wordPool.length - pre - 1)),
              preWords = wordPool.slice(pre, pre+preWordCount).join(' '),
              post = Math.trunc(Math.random()*wordPool.length),
              postWordCount = 1 + Math.trunc(Math.random()*(wordPool.length - pre - 1)),
              postWords = wordPool.slice(post, post+postWordCount).join(' ');
        return(
          <span key={e[0]}>
            {preWords}
            <span className="tagIcon" style={{color:e[1].color}} data-icon={e[1].icon}>
            </span>
            <span className="tag" style={{borderColor:e[1].color}}>
              {` some ${e[0]} `}
            </span>
            {postWords}
          </span>
        );
    });
    return <p className="exampleText">{fragments}</p>
  }
  
  entityListEntries(){
    const entries = this.props.scheme.map((e, i)=>(
      <li key={i}>
        <input type="color" 
               value={e[1].color} 
               className="colorScheme border"
               onChange={event=>this.handleValueChange(i, 'color', event.target.value)}>
        </input>
        <IconPicker icon={e[1].icon} iconKey={'icon'+i} onChange={icon=>this.handleValueChange(i, 'icon', icon)}/>
        <div className="form-group d-inline-block">
          <input type="text" 
                 className="form-control" 
                 id="staticEmail2" 
                 value={e[0]} 
                 onChange={event=>this.handleNameChange(i, event.target.value)}/>
        </div>
        <button type="button" 
                className="close" 
                aria-label="Close" 
                onClick={()=>this.handleRemoveEntry(i)}>
          <span aria-hidden="true">&times;</span>
        </button>
      </li>
    ));
    
    return entries;
  }
  
  entityNewEntryField(){
      return( 
        <li>
          <input type="color" 
                 value={this.state.color} 
                 className="colorScheme border"
                 onChange={event=>this.setState({color: event.target.value})}>
          </input>
          <IconPicker icon={this.state.icon} iconKey={'newicon'} onChange={icon=>this.setState({icon})}/>
          <div className="form-group d-inline-block">
            <input type="text" 
                   className="form-control" 
                   id="staticEmail2" 
                   value={this.state.name} 
                   onChange={event=>this.setState({name: event.target.value})}/>
          </div>
          <button type="button" className="btn btn-light ml-4" onClick={()=>this.handleAddEntity()}>Add</button>
      </li>
    );
    
  }
  
  handleAddEntity(){
    const newScheme = [...this.props.scheme, [this.state.name, {color:this.state.color, icon: this.state.icon}]];
    this.props.updateScheme(newScheme);
    this.setState(this.defState);
  }
  
  handleNameChange(index, newName){
    this.props.scheme[index][0] = newName;
    this.props.updateScheme(this.props.scheme);
  }
  
  handleRemoveEntry(index){
    this.props.scheme.splice(index,1);
    this.props.updateScheme(this.props.scheme);
  }
  
  handleValueChange(index, key, value){
    this.props.scheme[index][1][key] = value;
    this.props.updateScheme(this.props.scheme);
  }
  
  render(){
    return(
      <div>
        <div className="row mt-4 bg-light">
          <div className="col-2">
            <b>TEI entities</b>
          </div>
          <div className="col">
            TEI provides with unique identifiers for named entities which can be then made use of in 
            the platform. Choose what entities will be used in the project, and their color and icon scheme.
          </div>
        </div>
        <div className="row mt-4">
          <div className="col-2"></div>
          <div className="col">
            <label>Entities</label>
            <ul className="noListStyle">
                {this.entityListEntries()}
                {this.entityNewEntryField()}
            </ul>
          </div>
          <div className="col">
            <div className="form-group">
              <label htmlFor="projectDescription">Example text with current scheme</label>
              {this.createExampleParagraphs()}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default TEIentitiesSection;