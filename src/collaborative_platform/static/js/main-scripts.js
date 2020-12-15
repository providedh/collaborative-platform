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
            $('[js-createNewProjectInfo]').text(xhr.responseJSON.message)
            $('#createNewProjectInfo').modal('show');
        }
    });
})
$('[js-listFileVersions]').DataTable( {
    "searching": false,
    "processing": true,
    "serverSide": true,
    "ordering": false,
    "ajax": {
        "url": "/api/files/" + $('[js-listFileVersions]').attr('data-file-id') + "/versions/",
        "dataSrc": "data"
    },
    "columns": [
        {
            "data": "number",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<a href="/files/' + oData.file_id + '/version/' + oData.number + '/">'+ oData.number +'</a>');
            }
        },
    
        {
            "data": "creation_date",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html(moment(sData).format('DD.MM.YY, HH:mm'));
            }
        },

        {
            "data": "id",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<a href="/user/' + oData.created_by_id + '">'+ oData.created_by +'</a>');
            }
        },

        {
            "data": "upload",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<a href="/api/files/' + oData.file_id + '/version/' + oData.number + '/download/" class="tb-button"><i class="fa fa-download"></i></a>');
            }
        }

        ,
        {
            "data": "hash",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<div class="input-group input-group-sm"><input type="text" readonly class="form-control" value="'+sData+'"/><div class="input-group-append"><button class="btn btn-outline-info" js-copyHash type="button"><i class="fa fa-copy"/></button></div></div>');
            }
        }
    ],

    "drawCallback": function () {
        $('.dataTables_paginate > .pagination').addClass('pagination-sm');
        $("[js-listRecentActivities] thead").remove();
    }
} );


$(document).on('click', '[js-copyHash]', function() {
    $(this).parent().siblings('input').select()
    $(this).parent().siblings('input').setSelectionRange(0, 99999);
    document.execCommand("copy");
})
$('[js-listProjectsMine]').DataTable( {
    "ajax": {
        "url": "/api/projects/get_mine/",
        "dataSrc": "data"
    },
    "columns": [
        {
            "data": "title",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<a href="'+ $('[js-listProjectsMine]').attr('data-link-project') + '' + oData.id +'">' + sData + '</a>');
            }
        },
        {
            "data": "contributors",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                var html = '';

                for (item in sData) {
                    html += '<a href="'+ $('[js-listProjectsMine]').attr('data-link-contributor') + '' + sData[item].id +'">' + sData[item].first_name + ' ' + sData[item].last_name + '</a>';
                    if (item != sData.length - 1 ) {
                        html += ', '
                    }
                }

                $(nTd).html(html);
            }
        },
        {
            "data": "modification_date",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html(moment(sData).format('DD.MM.YY, HH:mm'));
            }
        }
    ],

    "drawCallback": function () {
        $('.dataTables_paginate > .pagination').addClass('pagination-sm');
    }
} ).on('init', function (e, settings, json) {
    if(json.entries === 0) {document.getElementById('no-projects-hint').classList.remove('d-none')}
});

$('[js-listProjectsPublic]').DataTable( {
    "ajax": {
        "url": "/api/projects/get_public/",
        "dataSrc": "data"
    },
    "columns": [
        {
            "data": "title",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<a href="'+ $('[js-listProjectsPublic]').attr('data-link-project') + '' + oData.id +'">' + sData + '</a>');
            }
        },
        {
            "data": "contributors",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                var html = '';

                for (item in sData) {
                    html += '<a href="'+ $('[js-listProjectsPublic]').attr('data-link-contributor') + '' + sData[item].id +'">' + sData[item].first_name + ' ' + sData[item].last_name + '</a>';
                    if (item != sData.length - 1 ) {
                        html += ', '
                    }
                }

                $(nTd).html(html);
            }
        },
        {
            "data": "modification_date",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html(moment(sData).format('DD.MM.YY, HH:mm'));
            }
        }
    ],

    "drawCallback": function () {
        $('.dataTables_paginate > .pagination').addClass('pagination-sm');
    }
} );

$('[js-listProjectsUsers]').DataTable( {
    "ajax": {
        "url": "/api/projects/get_users/" + $('[js-listProjectsUsers]').attr('data-user-id') + '/',
        "dataSrc": "data"
    },
    "columns": [
        {
            "data": "title",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<a href="'+ $('[js-listProjectsUsers]').attr('data-link-project') + '' + oData.id +'">' + sData + '</a>');
            }
        },
        {
            "data": "contributors",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                var html = '';

                for (item in sData) {
                    html += '<a href="'+ $('[js-listProjectsUsers]').attr('data-link-contributor') + '' + sData[item].id +'">' + sData[item].first_name + ' ' + sData[item].last_name + '</a>';
                    if (item != sData.length - 1 ) {
                        html += ', '
                    }
                }

                $(nTd).html(html);
            }
        },
        {
            "data": "modification_date",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html(moment(sData).format('DD.MM.YY, HH:mm'));
            }
        }
    ],

    "drawCallback": function () {
        $('.dataTables_paginate > .pagination').addClass('pagination-sm');
    }
} );
var recentActivities = $('[js-listRecentActivities]').DataTable( {
    "searching": false,
    "processing": true,
    "serverSide": true,
    "ordering": false,
    "ajax": {
        "url": "/api/projects/" + $('[js-listRecentActivities]').attr('data-project-id') + "/activities/",
        "dataSrc": "data"
    },
    "columns": [
        {
            "data": "id",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                var html = '';

                if (oData.user_id) {
                    html += '<a href="/user/' + oData.user_id + '/">' + oData.user_name + '</a> ';
                } else {
                    html += '<span>' + oData.user_name + '</span> ';
                }

                html += '<span>' + oData.action_text + '</span>';

                if (oData.related_file_id && oData.related_file_name) {
                    html += ' <a href="/files/' + oData.related_file_id + '/">' + oData.related_file_name + '</a>';
                } else if (oData.related_file_name) {
                    html += ' <span>' + oData.related_file_name + '</span>';
                }

                $(nTd).html(html);
            }
        },
    
        {
            "data": "date",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html(moment(sData).format('DD.MM.YY, HH:mm'));
            }
        }
    ],

    "drawCallback": function () {
        $('.dataTables_paginate > .pagination').addClass('pagination-sm');
        $("[js-listRecentActivities] thead").remove();
    }
} );
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
var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
});

var id = $('#files').attr('data-project-id');
var idFile = $('#filep').attr('data-project-id');
var idFiles = $('#filep').attr('data-files-id');
var draggableElements = {};

var options = {
    divID : 'files',
    filesData : '/api/files/get_tree/' + id,
    rowHeight : 35,
    showTotal : 15,
    paginate : false,
    paginateToggle : false,
    lazyLoad : true,
    // useDropzone : true,
    uploads: true,
    resolveUploadUrl: function(item) {
        return "/api/files/upload/" + item.data.id + "/";
    },
    dropzone: {
        url: "p",
        headers: {
            'X-CSRFToken': csrftoken
        },

    },
    uploadURL : "eee",
    allowMove : true,
    allowArrows : true,
    multiselect : true,
    hoverClass : 'tb-hover',
    moveClass : 'tb-draggable',
    resolveRows : function () {
        return [
            {
                data : "title",
                folderIcons : true,
                filter : true,
                css : 'tb-draggable',
                custom : function (row) {
                    return  (row.data.kind !== "folder") ? m("a[href='/files/" + row.data.id + "/']", { 'data-file-id' : row.data.id }, row.data.name) : m("span", { 'data-file-id' : row.data.id }, row.data.name)
                }
            },
            {
                data : "date",
                filter : true,
                custom : function (row) {
                    return (row.data.kind !== "folder") ? moment(row.data.date).format('DD.MM.YY, HH:mm') : ''
                }
            },
            {
                data : "action",
                sortInclude : false,
                filter : false,
                css : 'tb-actions',
                custom : function (row) {
                    var that = this;

                    var buttons = []

                    var downloadDirectoryButton = m("a.tb-button[href='/api/files/directory/" + row.data.id +  "/download']", {}, m("i", {'class': "fa fa-download"}));
                    var downloadFileButton = m("a.tb-button[href='/api/files/" + row.data.id +  "/download']", m("i", {'class': "fa fa-download"}));

                    var editButton = m("button.tb-button", {
                            onclick: function _editClick(e) {
                                e.stopPropagation();
                                var title = row.data.name;
                                var value = '';


                                var data = "d"
                                function update(e) {
                                    if (data.length < 5) data = e.target.value
                                }


                                var mithrilContent = m('div', [
                                    m('h3.break-word', 'Change name'),
                                    m('p', 'Old name: ' + title),
                                    m('p', 'New name:'),
                                    m('input.form-control', {oninput: function (e) {value = e.target.value}}  )
                                ]);

                                var mithrilButtons = m('div', [
                                    m('button', { 'class' : 'btn btn-default m-r-md', onclick : function() { that.modal.dismiss(); } }, 'Cancel'),
                                    m('button', { 'class' : 'btn btn-success', onclick : function() {

                                        var url = (row.data.kind !== "folder") ? '/api/files/' + row.data.id + '/rename/' : '/api/files/directory/' + row.data.id + '/rename/';

                                        $.ajax({
                                            type: "PUT",
                                            url: url + value,
                                            contentType : 'application/json',
                                            success: function(resultData){
                                                that.modal.dismiss();
                                                that.refreshData();
                                            }
                                        });

                                    }  }, 'OK')
                                ]);
                                that.modal.update(mithrilContent, mithrilButtons);
                            }
                        }, m("i", {'class': "fa fa-edit"}));

                    var createFolderButton = m("button.tb-button", {
                        onclick: function _createFolderClick(e) {
                            e.stopPropagation();
                            var value = '';
                            var mithrilContent = m('div', [
                                m('h3.break-word', 'Create folder'),
                                m('p', 'Name:'),
                                m('input', {class: 'form-control', oninput: function (e) {value = e.target.value}} )
                            ]);
                            var mithrilButtons = m('div', [
                                m('button', { 'class' : 'btn btn-default m-r-md', onclick : function() { that.modal.dismiss(); } }, 'Cancel'),
                                m('button', { 'class' : 'btn btn-success', onclick : function() {

                                    $.ajax({
                                        type: "PUT",
                                        url: '/api/files/directory/' + row.data.id + '/create_subdir/' + value,
                                        contentType : 'application/json',
                                        success: function(resultData){
                                            that.modal.dismiss();
                                            that.refreshData();
                                        }
                                    });

                                }  }, 'OK')
                            ]);
                            that.modal.update(mithrilContent, mithrilButtons);
                        }
                    }, m("i", {'class': "fa fa-folder"}));

                    var deleteButton = m("button.tb-button", {
                        onclick: function _deleteClick(e) {
                            e.stopPropagation();
                            var mithrilContent = m('div', [
                                m('h3.break-word', 'Delete "' + row.data.name + '"?'),
                                m('p', 'This action is irreversible.')
                            ]);
                            var mithrilButtons = m('div', [
                                m('button', { 'class' : 'btn btn-default m-r-md', onclick : function() { that.modal.dismiss(); } }, 'Cancel'),
                                m('button', { 'class' : 'btn btn-success', onclick : function() {
                                    var url = (row.data.kind !== "folder") ? '/api/files/' : '/api/files/directory/';

                                    $.ajax({
                                        type: "DELETE",
                                        url: url + row.data.id,
                                        contentType : 'application/json',
                                        success: function(resultData){
                                            that.modal.dismiss();
                                            that.refreshData();
                                        }
                                    });

                                }  }, 'OK')
                            ]);
                            that.modal.update(mithrilContent, mithrilButtons);
                        }
                    }, m("i", {'class': "fa fa-trash"}));

                    if (row.data.kind === "folder") {
                        buttons.push(downloadDirectoryButton);
                    } else {
                        buttons.push(downloadFileButton);
                    }

                    if (row.data.parent) {
                        buttons.push(editButton);
                    }

                    if (row.data.kind === "folder") {
                        buttons.push(createFolderButton);
                    }

                    if (row.data.parent) {
                        buttons.push(deleteButton);
                    }

                    return buttons;


                }
            }
        ];
    },
    dragEvents : {
        start : function(event, ui) {
            var folders = [];
            var files = [];

            if ($(event.target).parent().hasClass('tb-multiselect')) {
                $('.tb-multiselect').each(function(index) {
                    if ($(this).find('[data-file-id]').prop("tagName") === 'SPAN') {
                        folders.push($(this).find('[data-file-id]').attr('data-file-id'))
                    } else {
                        files.push($(this).find('[data-file-id]').attr('data-file-id'))
                    }
                })

            } else {
                if ($(event.target).find('[data-file-id]').prop("tagName") === 'SPAN') {
                    folders.push($(event.target).find('[data-file-id]').attr('data-file-id'))
                } else {
                    files.push($(event.target).find('[data-file-id]').attr('data-file-id'))
                }
            }

            if (folders.length) {
                draggableElements['directories'] = folders;
            }

            if (files.length) {
                draggableElements['files'] = files;
            }

            




        },
    },
    dropEvents : {
        drop : function(event) {
            var that = this;
            if ($(event.target).find('[data-file-id]').prop("tagName") === 'SPAN') {
                $.ajax({
                    type: "POST",
                    url: '/api/files/move/' + $(event.target).find('[data-file-id]').attr('data-file-id'),
                    contentType : 'application/json',
                    data: JSON.stringify(draggableElements),
                    success: function(resultData){
                        that.refreshData();
                    }
                });
            }
        }
    },
    hScroll : null,

    onselectrow : function (row){
        // console.log(row);
    },
    columnTitles : function() {
        return [{
            title: "Name",
            width: "62%",
            sortType: "text",
            sort: true
        }, {
            title: "Modified",
            width: "18%",
            sortType: "date",
            sort: true
        }, {
            title: "",
            width: "20%",
            sort: false
        }]
    },

    ondataload : function () {
        var tb = this,
            rowDiv = tb.select('.tb-row');

        rowDiv.first().find('.tb-toggle-icon').click();
        addFileDragFeedback()
    },

};

var optionsFile = {
    divID : 'filep',
    filesData : '/api/files/get_tree/' + idFile,
    rowHeight : 35,
    showTotal : 15,
    paginate : false,
    paginateToggle : false,
    lazyLoad : false,
    uploads: false,
    showFilter : false,
    allowMove : false,
    allowArrows : true,
    multiselect : false,
    hoverClass : 'tb-hover',
    moveClass : 'tb-draggable',
    hScroll : null,
    resolveRows : function () {
        return [
            {
                data : "title",
                folderIcons : true,
                filter : true,
                css : 'tb-draggable',
                custom : function (row) {
                    return  (row.data.kind !== "folder") ? m("a[href='/files/" + row.data.id + "/']", { 'js-contentFileTree' : row.data.id }, row.data.name) : m("span", row.data.name)
                }
            }
        ];
    },

    columnTitles : function() {
        return [{
            title: "Name",
            width: "100%",
            sortType: "text",
            sort: false
        }]
    },

    ondataload : function (e) {
        var tb = this;

        tb.toggleFolder(0, false, false)

        function getIdFile(element) {
            if (element.row.id === parseInt(idFiles)) return element
        }

        var id = tb.flatData.find(getIdFile).id
        var findId = tb.find(id)
        var parId = findId.parentID

        arrayNestedOpen = [];

        do {
            if ( parId > 1 ){
                arrayNestedOpen.push(parId)
            }

            findId = tb.find(parId)
            parId = findId.parentID
        }
        while (parId > 0)

        arrayNestedOpen = arrayNestedOpen.reverse()

        for (var i = 0; i < arrayNestedOpen.length; i++ ) {
            $('[data-id="' + arrayNestedOpen[i] + '"]').find('.tb-toggle-icon').click()
        }

    },

};

if ($('#files').length) {
    var tb = Treebeard(options);
}

if ($('#filep').length) {
    var tb2 = Treebeard(optionsFile);
}

function addFileDragFeedback() {
    Array.from(document.getElementsByClassName('ui-draggable-handle')).forEach(x => {
        x.addEventListener('dragover', e => x.parentNode.classList.add('fileOver'))
        x.addEventListener('dragend', e => x.parentNode.classList.remove('fileOver'))
        x.addEventListener('dragleave', e => x.parentNode.classList.remove('fileOver'))
        x.addEventListener('drop', e => x.parentNode.classList.remove('fileOver'))
})
}
