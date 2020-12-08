(() => {
  [...document.getElementById('app-params').children].forEach(param => {
    const name = param.id;
    window.p_raw = param.innerText
    const value = name === 'preferences' ? JSON.parse(param.innerText.replace(/\\u0022/g, '"')) : param.innerText;
    window[name] = value;
  })
})()