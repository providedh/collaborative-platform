export default function styleEntity (id, color, icon, css) {
  const greyBorder = `
        .renderEntity #${id}
        {
            border-color: lightgrey;
        }
    `
  const renderBefore = `
        .renderEntity #${id}::before
        {
            pointer-events: none;
            content:"";
            position: absolute;
            font-size: 0.9em;
            padding-top: 1.1em;
            color:grey;
            font-family: "Font Awesome 5 Free";
            font-weight: 900;
            min-width: 5em;
        }
    `
  const hideBorder = `
        #${id}
        {
            cursor: pointer;
            border-color: white;
        }
    `
  const renderEntity = `
        #${id}
        {
            border-bottom: solid 2px white;
            cursor: default;
            background-color: white;
            display: inline-block;
            height: 1.7em;
            position: relative;
        }
    `

  const colorBorder = `.renderEntity.colorEntity #${id}{ border-color: ${color};}`
  const entityIcon = `.renderEntity #${id}::before{ content: "${icon}";}`
  const colorEntityIcon = `.renderEntity.colorEntity #${id}::before{ color: ${color};}`

  const cssRules = [
    renderBefore,
    renderEntity,
    hideBorder,
    greyBorder,
    entityIcon,
    colorBorder,
    colorEntityIcon
  ].join('\n')

  css.addCode(cssRules)
}
