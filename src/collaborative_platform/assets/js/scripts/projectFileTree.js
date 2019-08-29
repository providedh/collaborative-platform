
var options = {
    divID : 'files',
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
        return [
            {
                data : "title",
                folderIcons : true,
                filter : true,
                css : 'tb-draggable'
            },
            {
                data : "date",
                filter : true,
                custom : function (row) {
                    console.log()
                    return (row.data.kind !== "folder") ? moment(row.data.date).format('DD.MM.YY, HH:mm') : ''
                }
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
                    }, m("i", {'class': "fa fa-trash"}));
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
    //hideColumnTitles : true,
    hScroll : null,
    hiddenFilterRows : ['person', 'age'],
    onselectrow : function (row){
        console.log(row);
    },
    columnTitles : function() {
        return [{
            title: "Name",
            width: "65%",
            sortType: "text",
            sort: true
        }, {
            title: "Modified",
            width: "25%",
            sortType: "date",
            sort: true
        }, {
            title: "",
            width: "10%",
            //sortType: "date",
            sort: false
        }]
    }

};

var tb = Treebeard(options);