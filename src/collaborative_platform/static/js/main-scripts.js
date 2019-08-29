$("#formCreateNewProject").on("submit",function(t){t.preventDefault();var e=$(this).serializeObject(),a=jQuery("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,e){t.setRequestHeader("X-CSRFToken",a)}}),$.ajax({type:"POST",url:"/api/projects/create/",data:JSON.stringify(e),dataType:"json",contentType:"application/json",success:function(t){window.location.href="/projects/"+t.id},error:function(t,e,a){$("#createNewProject").modal("hide"),$("[js-createNewProjectInfo]").text(t.responseJSON.message),$("#createNewProjectInfo").modal("show")}})}),$("[js-listProjectsMine]").DataTable({ajax:{url:"/api/projects/get_mine/",dataSrc:"data"},columns:[{data:"title",fnCreatedCell:function(t,e,a,o,i){$(t).html('<a href="'+$("[js-listProjectsMine]").attr("data-link-project")+a.id+'">'+e+"</a>")}},{data:"contributors",fnCreatedCell:function(t,e,a,o,i){var n="";for(item in e)n+='<a href="'+$("[js-listProjectsMine]").attr("data-link-contributor")+e[item].id+'">'+e[item].first_name+" "+e[item].last_name+"</a>",item!=e.length-1&&(n+=", ");$(t).html(n)}},{data:"modification_date",fnCreatedCell:function(t,e,a,o,i){$(t).html(moment(e).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm")}}),$("[js-listProjectsPublic]").DataTable({ajax:{url:"/api/projects/get_public/",dataSrc:"data"},columns:[{data:"title",fnCreatedCell:function(t,e,a,o,i){$(t).html('<a href="'+$("[js-listProjectsPublic]").attr("data-link-project")+a.id+'">'+e+"</a>")}},{data:"contributors",fnCreatedCell:function(t,e,a,o,i){var n="";for(item in e)n+='<a href="'+$("[js-listProjectsPublic]").attr("data-link-contributor")+e[item].id+'">'+e[item].first_name+" "+e[item].last_name+"</a>",item!=e.length-1&&(n+=", ");$(t).html(n)}},{data:"modification_date",fnCreatedCell:function(t,e,a,o,i){$(t).html(moment(e).format("DD.MM.YY, HH:mm"))}}],drawCallback:function(){$(".dataTables_paginate > .pagination").addClass("pagination-sm")}});var csrftoken=$("[name=csrfmiddlewaretoken]").val();$.ajaxSetup({beforeSend:function(t,e){t.setRequestHeader("X-CSRFToken",csrftoken)}}),$("[js-makePublicProject]").on("click",function(t){var e=$(this).attr("js-makePublicProject");$.ajax({type:"POST",url:"/api/projects/"+e+"/make_public",success:function(){$("[js-makePublicProject]").toggle2classes("project__button--makepublic","project__button--makepublic-active"),$("[js-makePrivateProject]").toggle2classes("project__button--makeprivate","project__button--makeprivate-active")}})}),$("[js-makePrivateProject]").on("click",function(t){var e=$(this).attr("js-makePrivateProject");$.ajax({type:"POST",url:"/api/projects/"+e+"/make_private",success:function(){$("[js-makePublicProject]").toggle2classes("project__button--makepublic","project__button--makepublic-active"),$("[js-makePrivateProject]").toggle2classes("project__button--makeprivate","project__button--makeprivate-active")}})});var options={divID:"files",filesData:"/static/tree.json",rowHeight:35,showTotal:15,paginate:!1,paginateToggle:!1,lazyLoad:!0,useDropzone:!0,uploadURL:"",allowMove:!0,allowArrows:!0,multiselect:!0,hoverClass:"hoverClass",moveClass:"tb-draggable",resolveRows:function(){return[{data:"title",folderIcons:!0,filter:!0,css:"tb-draggable"},{data:"date",filter:!0,custom:function(t){return console.log(),"folder"!==t.data.kind?moment(t.data.date).format("DD.MM.YY, HH:mm"):""}},{data:"action",sortInclude:!1,filter:!1,custom:function(t){var e=this;return m("button.tb-button",{onclick:function(a){a.stopPropagation();var o=m("div",[m("h3.break-word",'Delete "'+t.data.title+'"?'),m("p","This action is irreversible.")]),i=m("div",[m("button",{"class":"btn btn-default m-r-md",onclick:function(){e.modal.dismiss()}},"Cancel"),m("button",{"class":"btn btn-success",onclick:function(){e.deleteNode(t.parentID,t.id),e.modal.dismiss()}},"OK")]);e.modal.update(o,i)}},m("i",{"class":"fa fa-trash"}))}}]},dropEvents:{over:function(t,e){},drop:function(t,e){console.log("dropped",t,e),console.log($(e.draggable).text())}},hScroll:null,hiddenFilterRows:["person","age"],onselectrow:function(t){console.log(t)},columnTitles:function(){return[{title:"Name",width:"65%",sortType:"text",sort:!0},{title:"Modified",width:"25%",sortType:"date",sort:!0},{title:"",width:"10%",sort:!1}]}},tb=Treebeard(options);