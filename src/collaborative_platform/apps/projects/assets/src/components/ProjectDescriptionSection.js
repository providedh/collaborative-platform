import React from 'react';

class ProjectDescriptionSection extends React.Component {
  constructor(props){
    super(props);
  }
  
  createExampleParagraph(entity){
    
  }
  
  render(){
    return(
      <div className="row">
        <div className="col-2">
          <b>Project description</b>
        </div>
        <div className="col">
          <div className="form-group">
            <label htmlFor="projectTitle">Project title</label>
            <input type="text" 
                   className="form-control" 
                   name="title" 
                   id="projectTitle" 
                   placeholder="Enter project title" 
                   value={this.props.title}
                   onChange={e=>this.props.setTitle(e.target.value)}/>
          </div>
        </div>
        <div className="col">
          <div className="form-group">
            <label htmlFor="projectDescription">Project description</label>
            <textarea className="form-control" 
                      name="description" 
                      id="projectDescription" 
                      rows="3" 
                      placeholder="Enter project description"
                      value={this.props.description}
                      onChange={e=>this.props.setDescription(e.target.value)}></textarea>
          </div>
        </div>
      </div>
    ); 
  }
}

export default ProjectDescriptionSection;