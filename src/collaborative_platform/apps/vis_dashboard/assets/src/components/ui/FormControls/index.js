import ColorControl from './ColorControl'
import DocumentControl from './DocumentControl'
import CompactMultipleSelectionControl from './CompactMultipleSelectionControl'
import MultipleSelectionControl from './MultipleSelectionControl'
import NumberControl from './NumberControl'
import RangeControl from './RangeControl'
import SelectionControl from './SelectionControl'
import TextControl from './TextControl'
import ToogleControl from './ToogleControl'
import TextAreaControl from './TextAreaControl'

export default {
  color: ColorControl,
  documentId: DocumentControl,
  selection: SelectionControl,
  multipleSelection: MultipleSelectionControl,
  compactMultipleSelection: CompactMultipleSelectionControl,
  number: NumberControl,
  range: RangeControl,
  text: TextControl,
  textArea: TextAreaControl,
  toogle: ToogleControl
}
