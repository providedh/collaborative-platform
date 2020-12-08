(() => {
    [...document.getElementById('app-params').children].forEach(param => {
        const name = param.id;
        const jsonContent = t => JSON.parse(t.replace(/\\u0022/g, '"').replace(/\\u005C/g, '\\'));
        const value = name === 'preferences' ? jsonContent(param.innerText) : param.innerText;
        window[name] = value;
    });
    /*
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });
    */
})()