var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
});

var id = $('#files').attr('data-project-id');
var draggableElements = {};

var options = {
    divID : 'files',
    filesData : '/api/files/get_tree/' + id,
    rowHeight : 35,
    showTotal : 15,
    paginate : false,
    paginateToggle : false,
    lazyLoad : true,
    useDropzone : true,
    uploads: true,
    resolveUploadUrl: function(item) { // Allows the user to calculate the url of each individual row
        // this = treebeard object;
        // Item = item acted on return item.data.ursl.upload
        console.log(item)
        console.log(this)
        return "/api/files/upload/" + item.data.id + "/";
    },
    dropzone: {
        url: "http://www.torrentplease.com/dropzone.php",
        dragstart: function (treebeard, event) {
            // this = dropzone object
            // treebeard = treebeard object
            // event = event passed in
            window.console.log("dragstart", this, treebeard, event);
        },
    },
    uploadURL : "",
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
                    var downloadFileButton = m("a.tb-button[href='/api/files/" + row.data.id +  "/download']", m("i", {'class': "fa fa-edit"}));

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
    }

};

var tb = Treebeard(options);