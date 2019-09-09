$("#formCreateNewProject").on("submit",function(t){t.preventDefault();var a=$(this).serializeObject(),e=jQuery("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,a){t.setRequestHeader("X-CSRFToken",e)}}),$.ajax({type:"POST",url:"/api/projects/create/",data:JSON.stringify(a),dataType:"json",contentType:"application/json",success:function(t){window.location.href="/projects/"+t.id},error:function(t,a,e){$("#createNewProject").modal("hide"),$("[js-createNewProjectInfo]").text(t.responseJSON.message),$("#createNewProjectInfo").modal("show")}})}),$("[js-listProjectsMine]").DataTable({ajax:{url:"/api/projects/get_mine/",dataSrc:"data"},columns:[{data:"title",fnCreatedCell:function(t,a,e,i,n){$(t).html('<a href="'+$("[js-listProjectsMine]").attr("data-link-project")+e.id+'">'+a+"</a>")}},{data:"contributors",fnCreatedCell:function(t,a,e,i,n){var o="";for(item in a)o+='<a href="'+$("[js-listProjectsMine]").attr("data-link-contributor")+a[item].id+'">'+a[item].first_name+" "+a[item].last_name+"</a>",item!=a.length-1&&(o+=", ");$(t).html(o)}},{data:"modification_date",fnCreatedCell:function(t,a,e,i,n){$(t).html(moment(a).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm")}}),$("[js-listProjectsPublic]").DataTable({ajax:{url:"/api/projects/get_public/",dataSrc:"data"},columns:[{data:"title",fnCreatedCell:function(t,a,e,i,n){$(t).html('<a href="'+$("[js-listProjectsPublic]").attr("data-link-project")+e.id+'">'+a+"</a>")}},{data:"contributors",fnCreatedCell:function(t,a,e,i,n){var o="";for(item in a)o+='<a href="'+$("[js-listProjectsPublic]").attr("data-link-contributor")+a[item].id+'">'+a[item].first_name+" "+a[item].last_name+"</a>",item!=a.length-1&&(o+=", ");$(t).html(o)}},{data:"modification_date",fnCreatedCell:function(t,a,e,i,n){$(t).html(moment(a).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm")}}),$("[js-listRecentActivities]").DataTable({searching:!1,processing:!0,serverSide:!0,ordering:!1,ajax:{url:"/api/projects/"+$("[js-listRecentActivities]").attr("data-project-id")+"/activities/",dataSrc:"data"},columns:[{data:"id",fnCreatedCell:function(t,a,e,i,n){console.log(e);var o="";o+=e.user_id?'<a href="/user/'+e.user_id+'/">'+e.user_name+"</a> ":"<span>"+e.user_name+"</span> ",o+="<span>"+e.action_text+"</span>",e.related_file_id&&e.related_file_name?o+=' <a href="/user/'+e.related_file_id+'/">'+e.related_file_name+"</a>":e.related_file_name&&(o+=" <span>"+e.related_file_name+"</span>"),$(t).html(o)}},{data:"date",fnCreatedCell:function(t,a,e,i,n){$(t).html(moment(a).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm"),$("[js-listRecentActivities] thead").remove()}});var csrftoken=$("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,a){t.setRequestHeader("X-CSRFToken",csrftoken)}}),$("[js-makePublicProject]").on("click",function(t){var a=$(this).attr("js-makePublicProject");$.ajax({type:"POST",url:"/api/projects/"+a+"/make_public",success:function(){$("[js-makePublicProject]").toggle2classes("project__button--makepublic","project__button--makepublic-active"),$("[js-makePrivateProject]").toggle2classes("project__button--makeprivate","project__button--makeprivate-active")}})}),$("[js-makePrivateProject]").on("click",function(t){var a=$(this).attr("js-makePrivateProject");$.ajax({type:"POST",url:"/api/projects/"+a+"/make_private",success:function(){$("[js-makePublicProject]").toggle2classes("project__button--makepublic","project__button--makepublic-active"),$("[js-makePrivateProject]").toggle2classes("project__button--makeprivate","project__button--makeprivate-active")}})});var csrftoken=jQuery("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,a){t.setRequestHeader("X-CSRFToken",csrftoken)}});var id=$("#files").attr("data-project-id"),draggableElements={},options={divID:"files",filesData:"/api/files/get_tree/"+id,rowHeight:35,showTotal:15,paginate:!1,paginateToggle:!1,lazyLoad:!0,uploads:!0,resolveUploadUrl:function(t){return"/api/files/upload/"+t.data.id+"/"},dropzone:{url:"p",headers:{"X-CSRFToken":csrftoken},dragstart:function(t,a){window.console.log("dragstart",this,t,a)},dragend:function(t){console.log(t)}},uploadURL:"eee",allowMove:!0,allowArrows:!0,multiselect:!0,hoverClass:"tb-hover",moveClass:"tb-draggable",resolveRows:function(){return[{data:"title",folderIcons:!0,filter:!0,css:"tb-draggable",custom:function(t){return"folder"!==t.data.kind?m("a[href='/files/"+t.data.id+"/']",{"data-file-id":t.data.id},t.data.name):m("span",{"data-file-id":t.data.id},t.data.name)}},{data:"date",filter:!0,custom:function(t){return"folder"!==t.data.kind?moment(t.data.date).format("DD.MM.YY, HH:mm"):""}},{data:"action",sortInclude:!1,filter:!1,css:"tb-actions",custom:function(t){var a=this,e=[],i=m("a.tb-button[href='/api/files/directory/"+t.data.id+"/download']",{},m("i",{"class":"fa fa-download"})),n=m("a.tb-button[href='/api/files/"+t.data.id+"/download']",m("i",{"class":"fa fa-edit"})),o=m("button.tb-button",{onclick:function(e){e.stopPropagation();var i=t.data.name,n="",o=m("div",[m("h3.break-word","Change name"),m("p","Old name: "+i),m("p","New name:"),m("input.form-control",{oninput:function(t){n=t.target.value}})]),r=m("div",[m("button",{"class":"btn btn-default m-r-md",onclick:function(){a.modal.dismiss()}},"Cancel"),m("button",{"class":"btn btn-success",onclick:function(){var e="folder"!==t.data.kind?"/api/files/"+t.data.id+"/rename/":"/api/files/directory/"+t.data.id+"/rename/";$.ajax({type:"PUT",url:e+n,contentType:"application/json",success:function(t){a.modal.dismiss(),a.refreshData()}})}},"OK")]);a.modal.update(o,r)}},m("i",{"class":"fa fa-edit"})),r=m("button.tb-button",{onclick:function(e){e.stopPropagation();var i="",n=m("div",[m("h3.break-word","Create folder"),m("p","Name:"),m("input",{"class":"form-control",oninput:function(t){i=t.target.value}})]),o=m("div",[m("button",{"class":"btn btn-default m-r-md",onclick:function(){a.modal.dismiss()}},"Cancel"),m("button",{"class":"btn btn-success",onclick:function(){$.ajax({type:"PUT",url:"/api/files/directory/"+t.data.id+"/create_subdir/"+i,contentType:"application/json",success:function(t){a.modal.dismiss(),a.refreshData()}})}},"OK")]);a.modal.update(n,o)}},m("i",{"class":"fa fa-folder"})),s=m("button.tb-button",{onclick:function(e){e.stopPropagation();var i=m("div",[m("h3.break-word",'Delete "'+t.data.name+'"?'),m("p","This action is irreversible.")]),n=m("div",[m("button",{"class":"btn btn-default m-r-md",onclick:function(){a.modal.dismiss()}},"Cancel"),m("button",{"class":"btn btn-success",onclick:function(){var e="folder"!==t.data.kind?"/api/files/":"/api/files/directory/";$.ajax({type:"DELETE",url:e+t.data.id,contentType:"application/json",success:function(t){a.modal.dismiss(),a.refreshData()}})}},"OK")]);a.modal.update(i,n)}},m("i",{"class":"fa fa-trash"}));return"folder"===t.data.kind?e.push(i):e.push(n),t.data.parent&&e.push(o),"folder"===t.data.kind&&e.push(r),t.data.parent&&e.push(s),e}}]},dragEvents:{start:function(t,a){var e=[],i=[];$(t.target).parent().hasClass("tb-multiselect")?$(".tb-multiselect").each(function(t){"SPAN"===$(this).find("[data-file-id]").prop("tagName")?e.push($(this).find("[data-file-id]").attr("data-file-id")):i.push($(this).find("[data-file-id]").attr("data-file-id"))}):"SPAN"===$(t.target).find("[data-file-id]").prop("tagName")?e.push($(t.target).find("[data-file-id]").attr("data-file-id")):i.push($(t.target).find("[data-file-id]").attr("data-file-id")),e.length&&(draggableElements.directories=e),i.length&&(draggableElements.files=i)}},dropEvents:{drop:function(t){var a=this;"SPAN"===$(t.target).find("[data-file-id]").prop("tagName")&&$.ajax({type:"POST",url:"/api/files/move/"+$(t.target).find("[data-file-id]").attr("data-file-id"),contentType:"application/json",data:JSON.stringify(draggableElements),success:function(t){a.refreshData()}})}},hScroll:null,onselectrow:function(t){},columnTitles:function(){return[{title:"Name",width:"62%",sortType:"text",sort:!0},{title:"Modified",width:"18%",sortType:"date",sort:!0},{title:"",width:"20%",sort:!1}]}},tb=Treebeard(options);