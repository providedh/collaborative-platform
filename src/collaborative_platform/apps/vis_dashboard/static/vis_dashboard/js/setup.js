(() => {
    [...document.getElementById('app-params').children].forEach(param => {
      const name = param.id;
      const value = name === 'config' ? JSON.parse(param.innerText.replace(/&quot;/g, '"')) : param.innerText;
      window[name] = value;
    })
  })()