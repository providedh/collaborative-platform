$('#listProjectsMine').DataTable( {
    "ajax": {
        "url": "/api/projects/get_mine/",
        "dataSrc": "data"
    },
    "columns": [
        { "data": "title" },
        { "data": "modification_date" }
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
        { "data": "title" },
        { "data": "modification_date" }
    ],
    "drawCallback": function () {
        $('.dataTables_paginate > .pagination').addClass('pagination-sm');
    }
} );