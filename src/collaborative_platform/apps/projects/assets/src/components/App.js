import React from 'react';

import taxonomy from './def_taxonomy.js';
import ProjectDescriptionSection from './ProjectDescriptionSection.js';
import TaxonomySection from './TaxonomySection.js';
import TEIentitiesSection from './TEIentitiesSection.js';

class App extends React.Component {
  constructor(props){
    super(props);

    this.state = {
      title: '',
      description: '',
      certScheme: Object.entries(taxonomy.taxonomy),
      teiScheme: Object.entries(taxonomy.entities),
    };

    this.createProject = this.createProject.bind(this);
    this.updateCertScheme = this.updateCertScheme.bind(this);
    this.updateTEIScheme = this.updateTEIScheme.bind(this);
  }

  componentDidMount(){
    document.getElementById('create-project-button')
        .addEventListener('click', this.createProject);

  }

  updateCertScheme(scheme){
    this.setState({certScheme: scheme});
  }

  updateTEIScheme(scheme){
    this.setState({teiScheme: scheme});
  }

  validateScheme(){
    function hasEmptyNames(names){return names.some(x=>x.length == 0);}
    function hasRepeatedNames(names){return (new Set(names)).size != names.length;}
    
    const isValid = (true &&
      !hasEmptyNames(this.state.teiScheme.map(x=>x[0])) &&
      !hasRepeatedNames(this.state.teiScheme.map(x=>x[0])) &&
      !hasEmptyNames(this.state.certScheme.map(x=>x[0])) &&
      !hasRepeatedNames(this.state.certScheme.map(x=>x[0])));

    return isValid;
  }

  createProject(e){
    e.preventDefault()
    const key2name = array=>({...array[1], name:array[0]});
    const body_list2boolean = ({name, color, icon, body_list})=>
      ({name, color, icon, body_list:body_list=='true'})

    if(this.validateScheme() === false)
      return;

    const data = {
      title: this.state.title,
      description: this.state.description,
      taxonomy: this.state.certScheme.map(key2name),
      entities: this.state.teiScheme.map(key2name).map(body_list2boolean)
    };

    var form = $(this).serializeObject()
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

    $.ajax({
        type: "POST",
        url: "/api/projects/create/",
        data: JSON.stringify(data),
        dataType: "json",
        contentType : 'application/json',
        success: function(resultData){
            window.location.href = '/projects/' + resultData.id
        },
        error: function (xhr, ajaxOptions, thrownError) {
            $('#createNewProject').modal('hide');
            $('[js-createNewProjectInfo]').text(xhr.responseJSON.message)
            $('#createNewProjectInfo').modal('show');
        }
    });
  }

  render(){
    return(
      <div>
        <ProjectDescriptionSection
          title={this.state.title}
          description={this.state.description}
          setTitle={title=>this.setState({title:title})}
          setDescription={description=>this.setState({description:description})}
          />
        <TEIentitiesSection
          scheme={this.state.teiScheme}
          updateScheme={this.updateTEIScheme}
          />
        <TaxonomySection
          scheme={this.state.certScheme}
          updateScheme={this.updateCertScheme}
          />
      </div>
    );
  }
}

export default App;