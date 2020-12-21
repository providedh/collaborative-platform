(() => {
    window.djangoAppConfig = {};
    [...document.getElementById('app-params').children].forEach(param => {
        const name = param.id;
        const jsonContent = t => (t
            .replace(/\\u0022/g, '"')
            .replace(/\\u0027/g, '"')
            .replace(/\\u005C/g, '\\'));

        const value = name === 'preferences' ? JSON.parse(jsonContent(param.innerText)) : param.innerText;
        window.djangoAppConfig[name] = value;
    });
})()