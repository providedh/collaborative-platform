export const aScheme = {
  colorBefore: (id, annotations, currentUser, css, colorForUncertainty, taxonomy) => {
    return ''
  },
  colorContent: (id, annotations, currentUser, css, colorForUncertainty, taxonomy) => {
    const annotationsFlattened = []
    annotations.forEach(annotation => {
      annotation.ana.split(' ').forEach(category => {
        annotationsFlattened.push([category.split('#')[1], annotation.cert, annotation.resp, annotation['xml:id']])
      })
    })

    const gradStops = []
    const numberAnnotations = annotationsFlattened.length
    const color4author = (color, author, currentUser) => color
    const annotationSpacer = 10
    const percIncrement = (100 - numberAnnotations * annotationSpacer) / annotations.length// author=='#'+currentUser?'#fff0':'#ffff'

    const colors = annotationsFlattened.map(([category, cert, resp, id]) =>
      colorForUncertainty(category, cert, taxonomy))

    let curPercentage = percIncrement
    let prevAuthor, prevXmlid, prevColor, author, xmlid;
    [,, author] = annotationsFlattened[0]
    let color = color4author(colors[0], author, currentUser)
    gradStops.push(`${color} 0%`)

    for (let i = 1; i < annotationsFlattened.length; i++) {
      [,, prevAuthor, prevXmlid] = annotationsFlattened[i - 1]
      prevColor = color4author(colors[i - 1], prevAuthor, currentUser);
      [,, author, xmlid] = annotationsFlattened[i]
      color = color4author(colors[i], author, currentUser)

      if (xmlid !== prevXmlid) {
        gradStops.push(`${prevColor} ${curPercentage}%`)
        gradStops.push(`#fff ${curPercentage}%`)
        gradStops.push(`#fff ${curPercentage + annotationSpacer}%`)
        gradStops.push(`${color} ${curPercentage + annotationSpacer}%`)
        curPercentage += (annotationSpacer + percIncrement)
      } else {
        gradStops.push(`${prevColor} ${curPercentage}%`)
        gradStops.push(`${color} ${curPercentage}%`)
        curPercentage += percIncrement
      }
    }

    [,, author] = annotationsFlattened[annotationsFlattened.length - 1]
    color = color4author(colors[colors.length - 1], author, currentUser)
    gradStops.push(`${color} 100%`)

    const grad = css.createLinearGradient(gradStops)

    return grad
  },
  colorAfter: (id, annotations, currentUser, css, colorForUncertainty, taxonomy) => {
    return ''
  },
  greyBefore: (id, annotations, currentUser, css, colorForUncertainty, taxonomy) => {
    const node = document.getElementById(id)
    const numberAnnotations = annotations.length
    const style = window.getComputedStyle(node, '::before')
    const content = style.getPropertyValue('content')

    return `content: ${content.slice(0, -1)} ${'' + numberAnnotations} \\f591" !important;`
  },
  greyContent: (id, annotations, currentUser, css, colorForUncertainty, taxonomy) => {
    const annotationsFlattened = []
    annotations.forEach(annotation => {
      annotation.ana.split(' ').forEach(category => {
        annotationsFlattened.push([category.split('#')[1], annotation.cert, annotation.resp, annotation['xml:id']])
      })
    })

    const gradStops = []
    const numberAnnotations = annotationsFlattened.length
    const color4author = (color, author, currentUser) => 'lightgrey'
    const annotationSpacer = 10
    const percIncrement = (100 - numberAnnotations * annotationSpacer) / annotations.length// author=='#'+currentUser?'#fff0':'#ffff'

    const colors = annotationsFlattened.map(([category, cert, resp, id]) =>
      colorForUncertainty(category, cert, taxonomy))

    let curPercentage = percIncrement
    let prevAuthor, prevXmlid, prevColor, author, xmlid;
    [,, author] = annotationsFlattened[0]
    let color = color4author(colors[0], author, currentUser)
    gradStops.push(`${color} 0%`)

    for (let i = 1; i < annotationsFlattened.length; i++) {
      [,, prevAuthor, prevXmlid] = annotationsFlattened[i - 1]
      prevColor = color4author(colors[i - 1], prevAuthor, currentUser);
      [,, author, xmlid] = annotationsFlattened[i]
      color = color4author(colors[i], author, currentUser)

      if (xmlid !== prevXmlid) {
        gradStops.push(`${prevColor} ${curPercentage}%`)
        gradStops.push(`#fff ${curPercentage}%`)
        gradStops.push(`#fff ${curPercentage + annotationSpacer}%`)
        gradStops.push(`${color} ${curPercentage + annotationSpacer}%`)
        curPercentage += (annotationSpacer + percIncrement)
      } else {
        gradStops.push(`${prevColor} ${curPercentage}%`)
        gradStops.push(`${color} ${curPercentage}%`)
        curPercentage += percIncrement
      }
    }

    [,, author] = annotationsFlattened[annotationsFlattened.length - 1]
    color = color4author(colors[colors.length - 1], author, currentUser)
    gradStops.push(`${color} 100%`)

    const grad = css.createLinearGradient(gradStops)

    return grad
  },
  greyAfter: (id, annotations, currentUser, css, colorForUncertainty, taxonomy) => {
    const annotationsFlattened = []
    annotations.forEach(annotation => {
      annotation.ana.split(' ').forEach(category => {
        annotationsFlattened.push([category.split('#')[1], annotation.cert, annotation.resp, annotation['xml:id']])
      })
    })

    const gradStops = []
    const numberAnnotations = annotationsFlattened.length
    const color4author = (color, author, currentUser) => author === currentUser ? '#fff0' : '#ffff'
    const annotationSpacer = 10
    const percIncrement = (100 - numberAnnotations * annotationSpacer) / annotations.length// author=='#'+currentUser?'#fff0':'#ffff'

    const colors = annotationsFlattened.map(([category, cert, resp, id]) =>
      colorForUncertainty(category, cert, taxonomy))

    let curPercentage = percIncrement
    let prevAuthor, prevXmlid, prevColor, author, xmlid;
    [,, author] = annotationsFlattened[0]
    let color = color4author(colors[0], author, currentUser)
    gradStops.push(`${color} 0%`)

    for (let i = 1; i < annotationsFlattened.length; i++) {
      [,, prevAuthor, prevXmlid] = annotationsFlattened[i - 1]
      prevColor = color4author(colors[i - 1], prevAuthor, currentUser);
      [,, author, xmlid] = annotationsFlattened[i]
      color = color4author(colors[i], author, currentUser)

      if (xmlid !== prevXmlid) {
        gradStops.push(`${prevColor} ${curPercentage}%`)
        gradStops.push(`#fff ${curPercentage}%`)
        gradStops.push(`#fff ${curPercentage + annotationSpacer}%`)
        gradStops.push(`${color} ${curPercentage + annotationSpacer}%`)
        curPercentage += (annotationSpacer + percIncrement)
      } else {
        gradStops.push(`${prevColor} ${curPercentage}%`)
        gradStops.push(`${color} ${curPercentage}%`)
        curPercentage += percIncrement
      }
    }

    [,, author] = annotationsFlattened[annotationsFlattened.length - 1]
    color = color4author(colors[colors.length - 1], author, currentUser)
    gradStops.push(`${color} 100%`)

    const grad = css.createLinearGradient(gradStops)

    return ("content: '';" +
      'width: 100%;' +
        'position: absolute;' +
        'left: 0;' +
        'top: 0;' +
        'height: 35%;' +
      grad)
  }
}
