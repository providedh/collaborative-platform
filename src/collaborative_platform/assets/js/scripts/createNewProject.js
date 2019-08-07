$('[js-createNewProject]').on('click', function(){
    var form = $('#formCreateNewProject').serializeObject()
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

    $.ajax({
        type: "POST",
        url: "/api/projects/create/",
        data: JSON.stringify(form),
        dataType: "text",
        contentType : 'application/json',
        success: function(resultData){
            $('#createNewProject').modal('hide');
            $('[js-createNewProjectInfo]').text(resultData)
            $('#createNewProjectInfo').modal('show');
        },
        error: function (xhr, ajaxOptions, thrownError) {
            $('#createNewProject').modal('hide');
            $('[js-createNewProjectInfo]').text(thrownError)
            $('#createNewProjectInfo').modal('show');
        }
    });
})