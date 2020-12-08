(() => {
    [...document.getElementById('app-params').children].forEach(param => {
        const name = param.id;
        const value = name === 'preferences' ? JSON.parse(param.innerText.replace(/\\u0022/g, '"')) : param.innerText;
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