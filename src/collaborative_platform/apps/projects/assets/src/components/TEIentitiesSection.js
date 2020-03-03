import React from 'react';
import taxonomy from './def_taxonomy.js';

import IconPicker from './IconPicker.js';

class TEIentitiesSection extends React.PureComponent {
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
            <span className="entity">
              <span className="tagIcon" style={{color:e[1].color}} data-icon={e[1].icon}>
              </span>
              <span className="tag" style={{borderColor:e[1].color}}>
                {` some ${e[0]} `}
              </span>
            </span>
            {postWords}
          </span>
        );
    });
    return <p className="exampleText">{fragments}</p>
  }
  
  entityListEntries(){
    const propertyList = (e) => (!e.hasOwnProperty('properties'))?'':
      <p className="px-5 text-muted small mb-0">This entity has: {e.properties.join(', ')}</p>;

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
                 value={e[0]} 
                 onChange={event=>this.handleNameChange(i, event.target.value)}/>
        </div>
        <button type="button" 
                className="close" 
                aria-label="Close" 
                onClick={()=>this.handleRemoveEntry(i)}>
          <span aria-hidden="true">&times;</span>
        </button>
        {propertyList(e[1])}
        <div className="small d-block px-5">
          <span>List existing {e[0]}s in the documents?</span>
          <div className="form-check form-check-inline">
            <input className="form-check-input" type="radio" name={e[0]+'list'} id={e[0]+'showList'} value={true}/>
            <label className="form-check-label" htmlFor={e[0]+'showList'}>yes</label>
          </div>
          <div className="form-check form-check-inline">
            <input className="form-check-input" type="radio" name={e[0]+'list'} id={e[0]+'hideList'} value={false}/>
            <label className="form-check-label" htmlFor={e[0]+'hideList'}>no</label>
          </div>
        </div>
        <hr />
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
    const newEntity = [this.state.name, {color:this.state.color, icon: this.state.icon}];
    if(taxonomy.entities.hasOwnProperty(this.state.name) &&
        taxonomy.entities[this.state.name].hasOwnProperty('properties')){
      newEntity[1].properties = taxonomy.entities[this.state.name].properties;
    }

    const newScheme = [...this.props.scheme, newEntity];
    this.props.updateScheme(newScheme);
    this.setState(this.defState);
  }
  
  handleNameChange(index, newName){
    const newValue = this.props.scheme[index];
    newValue[0] = newName;
    const newScheme = this.props.scheme.map((x,i)=>i!=index?x:newValue);
    this.props.updateScheme(newScheme);
  }
  
  handleRemoveEntry(index){
    const newScheme = this.props.scheme.map(x=>x);
    newScheme.splice(index,1);
    this.props.updateScheme(newScheme);
  }
  
  handleValueChange(index, key, value){
    const newValue = this.props.scheme[index];
    newValue[1][key] = value;
    const newScheme = this.props.scheme.map((x,i)=>i!=index?x:newValue);
    this.props.updateScheme(newScheme);
  }
  
  render(){
    return(
      <div>
        <div id="teiSection" className="row mt-4 bg-light">
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