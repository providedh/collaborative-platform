function contentFile(t){var e=$("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,a){t.setRequestHeader("X-CSRFToken",e)}}),window.history.replaceState(null,null,"/files/"+t),$.ajax({type:"GET",url:"/api/files/"+t,contentType:"application/json",success:function(e){console.log(e);var a=Prism.highlight(e.data,Prism.languages.xml,"xml");$("[js-contentFile]").html(a),$("[js-contentFileName]").text(e.filename),$("[js-contentFileVersion]").text(e.version_number),$("[js-contentFileCreator]").html('<a href="/user/'+e.creator.id+'">'+e.creator.first_name+" "+e.creator.last_name+"</a>"),$("[js-contentFileCheckout]").attr("js-contentFileCheckout",t),$("[js-contentFileDelete]").attr("js-contentFileDelete",t),$("[js-contentFileDownload]").attr("js-contentFileDownload",t),$("[js-contentFileRevisions]").attr("js-contentFileRevisions",t),$("[js-contentFileCloseReading]").attr("js-contentFileCloseReading",t)},error:function(t,e,a){}})}$(document).ready(function(){if($("[js-contentFile]").length>0){var t=$("[js-contentFile]").attr("js-contentFile");contentFile(t)}}),$(document).on("click","[js-contentFileTree]",function(t){t.preventDefault();var e=$(this).attr("js-contentFileTree");contentFile(e)}),$(document).on("click","[js-contentFileCheckout]",function(t){t.preventDefault();$(this).attr("js-contentFileCheckout")}),$(document).on("click","[js-contentFileDelete]",function(t){t.preventDefault();var e=$(this).attr("js-contentFileDelete"),a=$("#filep").attr("data-project-id");$.ajax({type:"DELETE",url:"/api/files/"+e,contentType:"application/json",success:function(){$("#contentFileDelete").modal("hide"),window.location="/projects/"+a+"/"}})}),$(document).on("click","[js-contentFileDownload]",function(t){t.preventDefault();var e=$(this).attr("js-contentFileDownload");window.location="/api/files/"+e+"/download"}),$(document).on("click","[js-contentFileRevisions]",function(t){t.preventDefault();var e=$(this).attr("js-contentFileRevisions");window.location="/files/"+e+"/versions"}),$(document).on("click","[js-contentFileCloseReading]",function(t){t.preventDefault();var e=$(this).attr("js-contentFileCloseReading"),a=$("#filep").attr("data-project-id");window.location="/close_reading/project/"+a+"/file/"+e+"/"}),$("#formCreateNewProject").on("submit",function(t){t.preventDefault();var e=$(this).serializeObject(),a=jQuery("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,e){t.setRequestHeader("X-CSRFToken",a)}}),$.ajax({type:"POST",url:"/api/projects/create/",data:JSON.stringify(e),dataType:"json",contentType:"application/json",success:function(t){window.location.href="/projects/"+t.id},error:function(t,e,a){$("#createNewProject").modal("hide"),$("[js-createNewProjectInfo]").text(t.responseJSON.message),$("#createNewProjectInfo").modal("show")}})}),$("[js-listFileVersions]").DataTable({searching:!1,processing:!0,serverSide:!0,ordering:!1,ajax:{url:"/api/files/"+$("[js-listFileVersions]").attr("data-file-id")+"/versions/",dataSrc:"data"},columns:[{data:"number"},{data:"creation_date",fnCreatedCell:function(t,e,a,i,n){$(t).html(moment(e).format("DD.MM.YY, HH:mm"))}},{data:"id",fnCreatedCell:function(t,e,a,i,n){$(t).html('<a href="/user/'+a.created_by_id+'">'+a.created_by+"</a>")}},{data:"upload",fnCreatedCell:function(t,e,a,i,n){$(t).html('<a href="/'+a.upload+'" class="tb-button"><i class="fa fa-download"></i></a>')}},{data:"hash",fnCreatedCell:function(t,e,a,i,n){$(t).html('<div class="input-group input-group-sm"><input type="text" readonly class="form-control" value="'+e+'"/><div class="input-group-append"><button class="btn btn-outline-info" js-copyHash type="button"><i class="fa fa-copy"/></button></div></div>')}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm"),$("[js-listRecentActivities] thead").remove()}}),$(document).on("click","[js-copyHash]",function(){$(this).parent().siblings("input").select(),$(this).parent().siblings("input").setSelectionRange(0,99999),document.execCommand("copy")}),$("[js-listProjectsMine]").DataTable({ajax:{url:"/api/projects/get_mine/",dataSrc:"data"},columns:[{data:"title",fnCreatedCell:function(t,e,a,i,n){$(t).html('<a href="'+$("[js-listProjectsMine]").attr("data-link-project")+a.id+'">'+e+"</a>")}},{data:"contributors",fnCreatedCell:function(t,e,a,i,n){var o="";for(item in e)o+='<a href="'+$("[js-listProjectsMine]").attr("data-link-contributor")+e[item].id+'">'+e[item].first_name+" "+e[item].last_name+"</a>",item!=e.length-1&&(o+=", ");$(t).html(o)}},{data:"modification_date",fnCreatedCell:function(t,e,a,i,n){$(t).html(moment(e).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm")}}),$("[js-listProjectsPublic]").DataTable({ajax:{url:"/api/projects/get_public/",dataSrc:"data"},columns:[{data:"title",fnCreatedCell:function(t,e,a,i,n){$(t).html('<a href="'+$("[js-listProjectsPublic]").attr("data-link-project")+a.id+'">'+e+"</a>")}},{data:"contributors",fnCreatedCell:function(t,e,a,i,n){var o="";for(item in e)o+='<a href="'+$("[js-listProjectsPublic]").attr("data-link-contributor")+e[item].id+'">'+e[item].first_name+" "+e[item].last_name+"</a>",item!=e.length-1&&(o+=", ");$(t).html(o)}},{data:"modification_date",fnCreatedCell:function(t,e,a,i,n){$(t).html(moment(e).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm")}}),$("[js-listProjectsUsers]").DataTable({ajax:{url:"/api/projects/get_users/"+$("[js-listProjectsUsers]").attr("data-user-id")+"/",dataSrc:"data"},columns:[{data:"title",fnCreatedCell:function(t,e,a,i,n){$(t).html('<a href="'+$("[js-listProjectsUsers]").attr("data-link-project")+a.id+'">'+e+"</a>")}},{data:"contributors",fnCreatedCell:function(t,e,a,i,n){var o="";for(item in e)o+='<a href="'+$("[js-listProjectsUsers]").attr("data-link-contributor")+e[item].id+'">'+e[item].first_name+" "+e[item].last_name+"</a>",item!=e.length-1&&(o+=", ");$(t).html(o)}},{data:"modification_date",fnCreatedCell:function(t,e,a,i,n){$(t).html(moment(e).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm")}}),$("[js-listRecentActivities]").DataTable({searching:!1,processing:!0,serverSide:!0,ordering:!1,ajax:{url:"/api/projects/"+$("[js-listRecentActivities]").attr("data-project-id")+"/activities/",dataSrc:"data"},columns:[{data:"id",fnCreatedCell:function(t,e,a,i,n){var o="";o+=a.user_id?'<a href="/user/'+a.user_id+'/">'+a.user_name+"</a> ":"<span>"+a.user_name+"</span> ",o+="<span>"+a.action_text+"</span>",a.related_file_id&&a.related_file_name?o+=' <a href="/files/'+a.related_file_id+'/">'+a.related_file_name+"</a>":a.related_file_name&&(o+=" <span>"+a.related_file_name+"</span>"),$(t).html(o)}},{data:"date",fnCreatedCell:function(t,e,a,i,n){$(t).html(moment(e).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm"),$("[js-listRecentActivities] thead").remove()}});var csrftoken=$("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,e){t.setRequestHeader("X-CSRFToken",csrftoken)}}),$("[js-makePublicProject]").on("click",function(t){var e=$(this).attr("js-makePublicProject");$.ajax({type:"POST",url:"/api/projects/"+e+"/make_public",success:function(){$("[js-makePublicProject]").toggle2classes("project__button--makepublic","project__button--makepublic-active"),$("[js-makePrivateProject]").toggle2classes("project__button--makeprivate","project__button--makeprivate-active")}})}),$("[js-makePrivateProject]").on("click",function(t){var e=$(this).attr("js-makePrivateProject");$.ajax({type:"POST",url:"/api/projects/"+e+"/make_private",success:function(){$("[js-makePublicProject]").toggle2classes("project__button--makepublic","project__button--makepublic-active"),$("[js-makePrivateProject]").toggle2classes("project__button--makeprivate","project__button--makeprivate-active")}})});var csrftoken=jQuery("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,e){t.setRequestHeader("X-CSRFToken",csrftoken)}});var id=$("#files").attr("data-project-id"),idFile=$("#filep").attr("data-project-id"),draggableElements={},options={divID:"files",filesData:"/api/files/get_tree/"+id,rowHeight:35,showTotal:15,paginate:!1,paginateToggle:!1,lazyLoad:!0,uploads:!0,resolveUploadUrl:function(t){return"/api/files/upload/"+t.data.id+"/"},dropzone:{url:"p",headers:{"X-CSRFToken":csrftoken}},uploadURL:"eee",allowMove:!0,allowArrows:!0,multiselect:!0,hoverClass:"tb-hover",moveClass:"tb-draggable",resolveRows:function(){return[{data:"title",folderIcons:!0,filter:!0,css:"tb-draggable",custom:function(t){return"folder"!==t.data.kind?m("a[href='/files/"+t.data.id+"/']",{"data-file-id":t.data.id},t.data.name):m("span",{"data-file-id":t.data.id},t.data.name)}},{data:"date",filter:!0,custom:function(t){return"folder"!==t.data.kind?moment(t.data.date).format("DD.MM.YY, HH:mm"):""}},{data:"action",sortInclude:!1,filter:!1,css:"tb-actions",custom:function(t){var e=this,a=[],i=m("a.tb-button[href='/api/files/directory/"+t.data.id+"/download']",{},m("i",{"class":"fa fa-download"})),n=m("a.tb-button[href='/api/files/"+t.data.id+"/download']",m("i",{"class":"fa fa-download"})),o=m("button.tb-button",{onclick:function(a){a.stopPropagation();var i=t.data.name,n="",o=m("div",[m("h3.break-word","Change name"),m("p","Old name: "+i),m("p","New name:"),m("input.form-control",{oninput:function(t){n=t.target.value}})]),s=m("div",[m("button",{"class":"btn btn-default m-r-md",onclick:function(){e.modal.dismiss()}},"Cancel"),m("button",{"class":"btn btn-success",onclick:function(){var a="folder"!==t.data.kind?"/api/files/"+t.data.id+"/rename/":"/api/files/directory/"+t.data.id+"/rename/";$.ajax({type:"PUT",url:a+n,contentType:"application/json",success:function(t){e.modal.dismiss(),e.refreshData()}})}},"OK")]);e.modal.update(o,s)}},m("i",{"class":"fa fa-edit"})),s=m("button.tb-button",{onclick:function(a){a.stopPropagation();var i="",n=m("div",[m("h3.break-word","Create folder"),m("p","Name:"),m("input",{"class":"form-control",oninput:function(t){i=t.target.value}})]),o=m("div",[m("button",{"class":"btn btn-default m-r-md",onclick:function(){e.modal.dismiss()}},"Cancel"),m("button",{"class":"btn btn-success",onclick:function(){$.ajax({type:"PUT",url:"/api/files/directory/"+t.data.id+"/create_subdir/"+i,contentType:"application/json",success:function(t){e.modal.dismiss(),e.refreshData()}})}},"OK")]);e.modal.update(n,o)}},m("i",{"class":"fa fa-folder"})),l=m("button.tb-button",{onclick:function(a){a.stopPropagation();var i=m("div",[m("h3.break-word",'Delete "'+t.data.name+'"?'),m("p","This action is irreversible.")]),n=m("div",[m("button",{"class":"btn btn-default m-r-md",onclick:function(){e.modal.dismiss()}},"Cancel"),m("button",{"class":"btn btn-success",onclick:function(){var a="folder"!==t.data.kind?"/api/files/":"/api/files/directory/";$.ajax({type:"DELETE",url:a+t.data.id,contentType:"application/json",success:function(t){e.modal.dismiss(),e.refreshData()}})}},"OK")]);e.modal.update(i,n)}},m("i",{"class":"fa fa-trash"}));return"folder"===t.data.kind?a.push(i):a.push(n),t.data.parent&&a.push(o),"folder"===t.data.kind&&a.push(s),t.data.parent&&a.push(l),a}}]},dragEvents:{start:function(t,e){var a=[],i=[];$(t.target).parent().hasClass("tb-multiselect")?$(".tb-multiselect").each(function(t){"SPAN"===$(this).find("[data-file-id]").prop("tagName")?a.push($(this).find("[data-file-id]").attr("data-file-id")):i.push($(this).find("[data-file-id]").attr("data-file-id"))}):"SPAN"===$(t.target).find("[data-file-id]").prop("tagName")?a.push($(t.target).find("[data-file-id]").attr("data-file-id")):i.push($(t.target).find("[data-file-id]").attr("data-file-id")),a.length&&(draggableElements.directories=a),i.length&&(draggableElements.files=i)}},dropEvents:{drop:function(t){var e=this;"SPAN"===$(t.target).find("[data-file-id]").prop("tagName")&&$.ajax({type:"POST",url:"/api/files/move/"+$(t.target).find("[data-file-id]").attr("data-file-id"),contentType:"application/json",data:JSON.stringify(draggableElements),success:function(t){e.refreshData()}})}},hScroll:null,onselectrow:function(t){},columnTitles:function(){return[{title:"Name",width:"62%",sortType:"text",sort:!0},{title:"Modified",width:"18%",sortType:"date",sort:!0},{title:"",width:"20%",sort:!1}]},ondataload:function(){var t=this,e=t.select(".tb-row");e.first().find(".tb-toggle-icon").click()}},optionsFile={divID:"filep",filesData:"/api/files/get_tree/"+idFile,rowHeight:35,showTotal:15,paginate:!1,paginateToggle:!1,lazyLoad:!0,uploads:!1,showFilter:!1,allowMove:!1,allowArrows:!0,multiselect:!1,hoverClass:"tb-hover",moveClass:"tb-draggable",hScroll:null,resolveRows:function(){return[{data:"title",folderIcons:!0,filter:!0,css:"tb-draggable",custom:function(t){return"folder"!==t.data.kind?m("a[href='/files/"+t.data.id+"/']",{"js-contentFileTree":t.data.id},t.data.name):m("span",t.data.name)}}]},columnTitles:function(){return[{title:"Name",width:"100%",sortType:"text",sort:!1}]}};if($("#files").length)var tb=Treebeard(options);if($("#filep").length)var tb2=Treebeard(optionsFile);