import xml from 'common/helpers/xml.js'

function contentsFromRange (range) {
  const fragment = range.cloneRange().cloneContents()
  const container = document.createElement('div')
  container.appendChild(fragment)

  return container.innerHTML
}

function firstDisconcordance (str1, str2) {
  const maxLength = Math.max(str1.length, str2.length)
  for (let i = 0; i < maxLength; i++) {
    if (str1[i] !== str2[i]) return i
  }
  return maxLength
}

function getRelativePosition (source, node, offset, originalContent) {
  const range = document.createRange()
  range.setStart(source, 0)
  range.setEnd(node, offset)
  const content = contentsFromRange(range)
  const collapsed = xml.extractAndCollapseTags(originalContent)(content)

  return firstDisconcordance(originalContent, collapsed)
}

export function getSelection (container, selection, originalContent) {
  const xmlidReplaced = xml.replaceXmlid(originalContent)

  const anchorOffset = getRelativePosition(
    container,
    selection.anchorNode,
    selection.anchorOffset,
    xmlidReplaced
  )

  const focusOffset = getRelativePosition(
    container,
    selection.focusNode,
    selection.focusOffset,
    xmlidReplaced
  )

  const [start, end] = (anchorOffset < focusOffset)
    ? [anchorOffset, focusOffset]
    : [focusOffset, anchorOffset]

  return [start, end]
}

export function processSelection (selectionEvent) {
  let selection, text

  if (window.getSelection) {
    selection = window.getSelection()
    text = selection.toString()
  } else if (document.selection && document.selection.type !== 'Control') {
    selection = document.selection
    text = document.selection.createRange().text
  }

  if (selection.isCollased === true) return [null, null]
  if (selection.toString().length === 0) return [null, null]

  return [selection, text]
}
