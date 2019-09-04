$('[js-listRecentActivities]').DataTable( {
    "searching": false,
    "processing": true,
    "serverSide": true,
    "ajax": {
        "url": "/api/projects/" + $('[js-listRecentActivities]').attr('data-project-id') + "/activities/",
        "dataSrc": "data"
    },
    "columns": [
        {
            "data": "action",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('');
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
    }
} );
