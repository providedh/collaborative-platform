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
                $(nTd).html('<a href="/' + oData.upload + '" class="tb-button"><i class="fa fa-download"></i></a>');
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