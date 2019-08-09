$('#formCreateNewProject').on('submit', function(e){
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
        data: JSON.stringify(form),
        dataType: "json",
        contentType : 'application/json',
        success: function(resultData){
            window.location.href = '/projects/' + resultData.id
        },
        error: function (xhr, ajaxOptions, thrownError) {
            $('#createNewProject').modal('hide');
            $('[js-createNewProjectInfo]').text(thrownError)
            $('#createNewProjectInfo').modal('show');
        }
    });
})