
var options1 = {
    divID : 'grid1',
    filesData : "/static/tree.json",
    rowHeight : 35,
    showTotal : 15,
    paginate : false,
    paginateToggle : false,
    lazyLoad : true,
    useDropzone : true,
    uploadURL : "",
    allowMove : true,
    multiselect : true,
    hoverClass : 'hoverClass',
    moveClass : 'tb-draggable',
    resolveRows : function () {
        return [            // Defines columns based on data
            {
                data : "title",  // Data field name
                folderIcons : true,
                filter : true,
                css : 'tb-draggable'
            },
            {
                data : "person",
                filter : true
            },
            {
                data : "age",
                filter : false
            },
            {
                data : "action",
                sortInclude : false,
                filter : false,
                custom : function (row) {
                    var that = this;
                    return m("button.tb-button", {
                        onclick: function _deleteClick(e) {
                            e.stopPropagation();
                            var mithrilContent = m('div', [
                                m('h3.break-word', 'Delete "' + row.data.title+ '"?'),
                                m('p', 'This action is irreversible.')
                            ]);
                            var mithrilButtons = m('div', [
                                m('button', { 'class' : 'btn btn-default m-r-md', onclick : function() { that.modal.dismiss(); } }, 'Cancel'),
                                m('button', { 'class' : 'btn btn-success', onclick : function() { that.deleteNode(row.parentID, row.id); that.modal.dismiss(); }  }, 'OK')
                            ]);
                            that.modal.update(mithrilContent, mithrilButtons, m("h3.modal-title", "Hello"));
                        }
                    }, " X ");
                }
            }
        ];
    },
    dropEvents : {
        over : function(event, ui) {
        },
        drop : function(event, ui) {
            console.log("dropped", event, ui);
            console.log($(ui.draggable).text());
        }
    },
    hideColumnTitles : true,
    hScroll : 300,
    resolveIcon : function(){ return false; }
}

var options2 = {
    divID : 'grid2',
    filesData : "/static/tree.json",
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
    hoverClass : 'hoverClass',
    moveClass : 'tb-draggable',
    resolveRows : function () {
        return [            // Defines columns based on data
            {
                data : "title",  // Data field name
                folderIcons : true,
                filter : true,
                css : 'tb-draggable'
            },
            {
                data : "action",
                sortInclude : false,
                filter : false,
                custom : function (row) {
                    var that = this;
                    return m("button.tb-button", {
                        onclick: function _deleteClick(e) {
                            e.stopPropagation();
                            var mithrilContent = m('div', [
                                m('h3.break-word', 'Delete "' + row.data.title+ '"?'),
                                m('p', 'This action is irreversible.')
                            ]);
                            var mithrilButtons = m('div', [
                                m('button', { 'class' : 'btn btn-default m-r-md', onclick : function() { that.modal.dismiss(); } }, 'Cancel'),
                                m('button', { 'class' : 'btn btn-success', onclick : function() { that.deleteNode(row.parentID, row.id); that.modal.dismiss(); }  }, 'OK')
                            ]);
                            that.modal.update(mithrilContent, mithrilButtons);
                        }
                    }, " X ");
                }
            }
        ];
    },
    dropEvents : {
        over : function(event, ui) {
        },
        drop : function(event, ui) {
            console.log("dropped", event, ui);
            console.log($(ui.draggable).text());
        }
    },
    hideColumnTitles : true,
    hScroll : null,
    hiddenFilterRows : ['person', 'age'],
    onselectrow : function (row){
        console.log(row);
    }
};


var options3 = {
    divID : 'grid1',
    filesData : "/static/tree.json",
    rowHeight : 35,
    showTotal : 15,
    paginate : false,
    paginateToggle : false,
    lazyLoad : true,
    useDropzone : true,
    uploadURL : "",
    allowMove : true,
    multiselect : true,
    hoverClass : 'hoverClass',
    moveClass : 'tb-draggable',
    resolveRows : function () {
        return [            // Defines columns based on data
            {
                data : "title",  // Data field name
                folderIcons : true,
                filter : true,
                css : 'tb-draggable'
            },
            {
                data : "dateCreated",
                filter : true
            },
            {
                data : "download",
                filter : false
            },
            {
                data : "category",
                sortInclude : false,
                filter : false

            }
        ];
    },
    dropEvents : {
        over : function(event, ui) {
        },
        drop : function(event, ui) {
            console.log("dropped", event, ui);
            console.log($(ui.draggable).text());
        }
    },
    hideColumnTitles : false,
    hScroll : 500,
    columnTitles : function() { // REQUIRED: Adjust this array based on data needs.
        return [{
            title: "Title",
            width: "50%",
            sortType: "text",
            sort: true
        }, {
            title: "Date",
            width: "25%",
            sortType: "date",
            sort: true
        }, {
            title: "Download",
            width: "10%",
            sortType: "number",
            sort: true
        }, {
            title: "Category",
            width: "15%",
            sortType: "text",
            sort: true
        }];
    }
};


/*
 *  User defined code to implement Treebeard anywhere on the page.
 */
var tb1 = Treebeard(options3);
//var tb2 = Treebeard(options2);
//var tb3 = Treebeard(options3);