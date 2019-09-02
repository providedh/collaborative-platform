var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
});

var id = $('#files').attr('data-project-id');
var draggableElements;

var options = {
    divID : 'files',
    filesData : '/api/files/get_tree/' + id,
    rowHeight : 35,
    showTotal : 15,
    paginate : false,
    paginateToggle : false,
    lazyLoad : true,
    useDropzone : true,
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
                    return  (row.data.kind !== "folder") ? m("a[href='/projects/']", row.data.name) : m("span", row.data.name)
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

                    if (row.data.parent) {
                        return (row.data.kind !== "folder") ? [editButton, deleteButton] : [editButton, createFolderButton, deleteButton];
                    } else {
                        return createFolderButton;
                    }


                }
            }
        ];
    },
    dragEvents : {
        start : function(event, ui) {
            console.log('start')
            $('.tb-multiselect').each(function(index) {
                console.log(this)
            })
        },
    },
    dropEvents : {

        over : function(event, ui) {
            //console.log(ui)
        },
        drop : function(event, ui) {
            //console.log(ui)
            //console.log(event)
            //var obj = ui.draggable
            //console.log(obj)

            //for (var i = 0, len = obj.length; i < len; i++) {
            //    console.log(obj[i].dataset.id);
            //}
        }
    },
    hScroll : null,
    onselectrow : function (row){
        //console.log(row);
    },
    columnTitles : function() {
        return [{
            title: "Name",
            width: "65%",
            sortType: "text",
            sort: true
        }, {
            title: "Modified",
            width: "18%",
            sortType: "date",
            sort: true
        }, {
            title: "",
            width: "17%",
            //sortType: "date",
            sort: false
        }]
    }

};

var tb = Treebeard(options);