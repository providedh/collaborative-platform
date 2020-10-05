import React from 'react';
import taxonomy from './def_taxonomy.js';

import IconPicker from './IconPicker.js';

class TEIentitiesSection extends React.PureComponent {
  constructor(props){
    super(props);
    
    this.defState = {
      icon: "\uf042",
      color: '#aaaaaa',
      name: '',
      body_list: "false"
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

  entityProperties(name){
    let properties = '';
    if(taxonomy.properties.hasOwnProperty(name)){
          properties = (<p className="px-5 text-muted small mb-0">
            This entity has: {taxonomy.properties[name].join(', ')}
          </p>);
        }
    return properties;
  }
  
  entityListEntries(){
    const names = this.props.scheme.map(x=>x[0]);
    const entries = this.props.scheme.map((e, i)=>{
      const isValid = e[0].length > 0 && names.reduce((ac,dc)=>ac+(dc==e[0]),0) == 1;
      let msg = '';
      if(!isValid && e[0].length==0)
        msg = "Entities can't be empty";
      else
        msg = "Entities can't be repeated";

      return(
      <li key={i}>
        <input type="color" 
               value={e[1].color} 
               className="colorScheme border"
               onChange={event=>this.handleValueChange(i, 'color', event.target.value)}>
        </input>
        <IconPicker icon={e[1].icon} iconKey={'icon'+i} onChange={icon=>this.handleValueChange(i, 'icon', icon)}/>
        <div className="form-group d-inline-flex flex-column">
          <input type="text" 
                 className={`form-control ${isValid?'':'is-invalid'}`}
                 value={e[0]} 
                 onChange={event=>this.handleNameChange(i, event.target.value)}/>
          {isValid?'':<div className="invalid-feedback">{msg}</div>}
        </div>
        {this.props.scheme.length==1?'':(
          <button type="button" 
                  className="close" 
                  aria-label="Close" 
                  onClick={()=>this.handleRemoveEntry(i)}>
            <span aria-hidden="true">&times;</span>
          </button>
        )}
        {this.entityProperties(e[0])}
        {
          ['date', 'time'].includes(e[0]) ? '' :
            <div className="small d-block px-5">
              <span className="d-block">List existing {e[0]}s in the documents?</span>
              <div className="form-check form-check-inline">
                <input className="form-check-input" 
                  checked={e[1].body_list == "true"} 
                  type="radio" 
                  name={e[0]+'list'+i} 
                  id={e[0]+'showList'+i} 
                  onChange={event=>this.handleBodyListChange(i, event.target.value)}
                  value="true"/>
                <label className="form-check-label" htmlFor={e[0]+'showList'+i}>yes</label>
              </div>
              <div className="form-check form-check-inline">
                <input className="form-check-input" 
                  checked={e[1].body_list == "false"} 
                  type="radio" 
                  name={e[0]+'list'+i} 
                  id={e[0]+'hideList'+i} 
                  onChange={event=>this.handleBodyListChange(i, event.target.value)}
                  value="false"/>
                  <label className="form-check-label" htmlFor={e[0]+'hideList'+i}>no</label>
              </div>
            </div>
        }
        <hr />
      </li>
    )});
    
    return entries;
  }
  
  entityNewEntryField(){
    const names = this.props.scheme.map(x=>x[0]),
      isInvalid = this.state.name.length > 0 && names.reduce((ac,dc)=>ac+(dc==this.state.name),0) > 0,
      msg = isInvalid?"Entities can't be repeated":'';

      return( 
        <li>
          <input type="color" 
                 value={this.state.color} 
                 className="colorScheme border"
                 onChange={event=>this.setState({color: event.target.value})}>
          </input>
          <IconPicker icon={this.state.icon} iconKey={'newicon'} onChange={icon=>this.setState({icon})}/>
          <div className="form-group d-inline-flex flex-column">
            <input type="text" 
                   className={`form-control ${isInvalid?'is-invalid':''}`}
                   value={this.state.name} 
                   onChange={event=>this.setState({name: event.target.value})}/>
            {isInvalid?<div className="invalid-feedback">{msg}</div>:''}
          </div>
          <button type="button" className="btn btn-light ml-3" onClick={()=>this.handleAddEntity()}>Add</button>
          <div className="small d-block px-5">
            <span className="d-block">List existing {this.state.name}s in the documents?</span>
            <div className="form-check form-check-inline">
              <input className="form-check-input" 
                checked={this.state.body_list == "true"} 
                onChange={()=>this.setState({body_list: "true"})}
                type="radio" 
                name={this.state.name+'list'} 
                id={this.state.name+'showList'}
                value="true"/>
              <label className="form-check-label" htmlFor='teiShow'>yes</label>
            </div>
            <div className="form-check form-check-inline">
              <input className="form-check-input" 
                checked={this.state.body_list == "false"} type="radio" 
                onChange={()=>this.setState({body_list: "false"})}
                name={this.state.name+'list'} 
                id={this.state.name+'hideList'}
                value="false"/>
              <label className="form-check-label" htmlFor='teiHide'>no</label>
            </div>
          </div>
      </li>
    );
    
  }
  
  handleAddEntity(){
    const {name, color, icon, body_list} = this.state;

    if(name.length == 0)
      return;

    const alreadyIncluded = this.props.scheme.some(([name,..._])=>name == this.state.name);
    if(alreadyIncluded===true)
      return;

    const newEntity = [name, {color, icon, body_list}];
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

  handleBodyListChange(index, body_list){
    const newValue = this.props.scheme[index];
    newValue[1].body_list = body_list;
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