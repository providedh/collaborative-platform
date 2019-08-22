$('#listProjectsMine').DataTable( {
    "ajax": {
        "url": "/api/projects/get_mine/",
        "dataSrc": "data"
    },
    "columns": [
        {
            "data": "title",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<a href="'+ $('#listProjectsMine').attr('data-link-project') + '' + oData.id +'">' + sData + '</a>');
            }
        },
        {
            "data": "contributors",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                var html = '';

                for (item in sData) {
                    html += '<a href="'+ $('#listProjectsMine').attr('data-link-contributor') + '' + sData[item].id +'">' + sData[item].first_name + ' ' + sData[item].last_name + '</a>';
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

$('#listProjectsPublic').DataTable( {
    "ajax": {
        "url": "/api/projects/get_public/",
        "dataSrc": "data"
    },
    "columns": [
        {
            "data": "title",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                $(nTd).html('<a href="'+ $('#listProjectsMine').attr('data-link-project') + '' + oData.id +'">' + sData + '</a>');
            }
        },
        {
            "data": "contributors",
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                var html = '';

                for (item in sData) {
                    html += '<a href="'+ $('#listProjectsMine').attr('data-link-contributor') + '' + sData[item].id +'">' + sData[item].first_name + ' ' + sData[item].last_name + '</a>';
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