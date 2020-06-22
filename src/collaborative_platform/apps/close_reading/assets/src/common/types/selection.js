export const SelectionType = {textSelection: 'text-selection', hover: 'hover', click: 'click'}
export function Selection (type, target, screenX, screenY) {
    return { type, target, screenX, screenY}
}