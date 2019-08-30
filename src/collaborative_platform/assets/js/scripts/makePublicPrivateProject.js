var csrftoken = $("[name=csrfmiddlewaretoken]").val();
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
});

$('[js-makePublicProject]').on('click', function(e){
    var projectId = $(this).attr('js-makePublicProject')

    $.ajax({
        type: "POST",
        url: '/api/projects/' + projectId + '/make_public',
        success: function(){
            $('[js-makePublicProject]').toggle2classes('project__button--makepublic', 'project__button--makepublic-active')
            $('[js-makePrivateProject]').toggle2classes('project__button--makeprivate', 'project__button--makeprivate-active')
        }
    });
})

$('[js-makePrivateProject]').on('click', function(e){
    var projectId = $(this).attr('js-makePrivateProject')

    $.ajax({
        type: "POST",
        url: '/api/projects/' + projectId + '/make_private',
        success: function(){
            $('[js-makePublicProject]').toggle2classes('project__button--makepublic', 'project__button--makepublic-active')
            $('[js-makePrivateProject]').toggle2classes('project__button--makeprivate', 'project__button--makeprivate-active')
        }
    });
})