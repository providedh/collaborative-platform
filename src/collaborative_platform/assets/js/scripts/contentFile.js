$(document).ready(function() {
    if($('[js-contentFile]').length > 0) {
        var fileId = $('[js-contentFile]').attr('js-contentFile');
        contentFile(fileId)
    }
});

function contentFile(id) {
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

    if (window.location.pathname.includes('/version/')){
        var url = "/api/files/" + id + "/version/" + $('[js-contentFileVersion]').text() + "/";
    }
    else{
        var url = "/api/files/" + id + "/";
    }

    $.ajax({
        type: "GET",
        url: url,
        contentType : 'application/json',
        success: function(resultData){
            var html = Prism.highlight(resultData.data, Prism.languages.xml, 'xml');
            $('[js-contentFile]').html(html);

            $('[js-contentFileName]').text(resultData.filename);
            $('[js-contentFileVersion]').text(resultData.version_number);
            $('[js-contentFileCreator]').html('<a href="/user/'+ resultData.creator.id +'">' + resultData.creator.first_name + ' ' + resultData.creator.last_name + '</a>');

            $('[js-contentFileCheckout]').attr('js-contentFileCheckout', id);
            $('[js-contentFileDelete]').attr('js-contentFileDelete', id);
            $('[js-contentFileDownload]').attr('js-contentFileDownload', id);
            $('[js-contentFileRevisions]').attr('js-contentFileRevisions', id);
            $('[js-contentFileCloseReading]').attr('js-contentFileCloseReading', id);
            
        },
        error: function (xhr, ajaxOptions, thrownError) {

        }
    });
}

$(document).on('click', '[js-contentFileTree]', function(e) {
    e.preventDefault()
    var id = $(this).attr('js-contentFileTree')
    contentFile(id)
})

$(document).on('click', '[js-contentFileCheckout]', function(e) {
    e.preventDefault()
    var id = $(this).attr('js-contentFileCheckout')

    //TODO BACKEND
    
    // $.ajax({
    //     type: "DELETE",
    //     url: "/api/files/" + id,
    //     contentType : 'application/json',
    //     success: function(){
    //         $('#contentFileDelete').modal('hide');
    //         window.location = "/projects/" + projectId + "/"
    //     }
    // });
})

$(document).on('click', '[js-contentFileDelete]', function(e) {
    e.preventDefault()
    var id = $(this).attr('js-contentFileDelete')
    var projectId = $('#filep').attr('data-project-id')

    $.ajax({
        type: "DELETE",
        url: "/api/files/" + id,
        contentType : 'application/json',
        success: function(){
            $('#contentFileDelete').modal('hide');
            window.location = "/projects/" + projectId + "/"
        }
    });
})

$(document).on('click', '[js-contentFileDownload]', function(e) {
    e.preventDefault()
    var id = $(this).attr('js-contentFileDownload')
    window.location = "/api/files/" + id +  "/download"
})

$(document).on('click', '[js-contentFileRevisions]', function(e) {
    e.preventDefault()
    var id = $(this).attr('js-contentFileRevisions')

    window.location = "/files/" + id + "/versions"
})

$(document).on('click', '[js-contentFileCloseReading]', function(e) {
    e.preventDefault()
    var id = $(this).attr('js-contentFileCloseReading')
    var projectId = $('#filep').attr('data-project-id')

    window.location = "/close_reading/project/" + projectId + "/file/" + id + "/"
})

