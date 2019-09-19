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