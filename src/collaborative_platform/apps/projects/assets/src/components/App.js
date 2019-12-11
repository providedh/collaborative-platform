import React from 'react';

import taxonomy from './def_taxonomy.js';
import ProjectDescriptionSection from './ProjectDescriptionSection.js';
import TaxonomySection from './TaxonomySection.js';

class App extends React.Component {
  constructor(props){
    super(props);

    this.state = {
      title: '',
      description: '',
      certScheme: Object.entries(taxonomy.taxonomy),
    };

    this.createProject = this.createProject.bind(this);
    this.updateCertScheme = this.updateCertScheme.bind(this);
  }

  componentDidMount(){
    document.getElementById('create-project-button')
        .addEventListener('click', this.createProject);

  }

  updateCertScheme(scheme){
    this.setState({certScheme: scheme});
  }

  createProject(e){
    const data = {
      title: this.state.title,
      description: this.state.description,
      categories: this.state.certScheme,
      taxonomy: {
              name_1: this.state.certScheme[0][0],
              color_1: this.state.certScheme[0][1].color,
              desc_1: this.state.certScheme[0][1].description,
              name_2: this.state.certScheme[1][0],
              color_2: this.state.certScheme[1][1].color,
              desc_2: this.state.certScheme[1][1].description,
              name_3: this.state.certScheme[2][0],
              color_3: this.state.certScheme[2][1].color,
              desc_3: this.state.certScheme[2][1].description,
              name_4: this.state.certScheme[3][0],
              color_4: this.state.certScheme[3][1].color,
              desc_4: this.state.certScheme[3][1].description
          }
    };

    e.preventDefault()
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
        <TaxonomySection
          scheme={this.state.certScheme}
          updateScheme={this.updateCertScheme}
          />
      </div>
    );
  }
}

export default App;