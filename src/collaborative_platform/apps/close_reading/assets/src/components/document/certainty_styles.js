import { aScheme as scheme } from './certainty_schemes.js'
import colorForUncertainty from './color_transparency.js'
import xml from 'common/helpers/xml.js'

export default function CertaintyStyler (id, annotations, context, css) {
  const { user, configuration } = context

  const colorSelector = `.renderCertainty.colorCertainty #${xml.replacedId(id)}`
  const greySelector = `.renderCertainty #${xml.replacedId(id)}`

  const greyBeforeRule = scheme.greyBefore(id, annotations, user, css, colorForUncertainty, configuration.taxonomy)
  css.addBeforeRule(greySelector, greyBeforeRule)

  const greyContentRule = scheme.greyContent(id, annotations, user, css, colorForUncertainty, configuration.taxonomy)
  css.addRule(greySelector, greyContentRule)

  const greyAfterRule = scheme.greyAfter(id, annotations, user, css, colorForUncertainty, configuration.taxonomy)
  css.addAfterRule(greySelector, greyAfterRule)

  const colorBeforeRule = scheme.colorBefore(id, annotations, user, css, colorForUncertainty, configuration.taxonomy)
  css.addBeforeRule(colorSelector, colorBeforeRule)

  const colorContentRule = scheme.colorContent(id, annotations, user, css, colorForUncertainty, configuration.taxonomy)
  css.addRule(colorSelector, colorContentRule)

  const colorAfterRule = scheme.colorAfter(id, annotations, user, css, colorForUncertainty, configuration.taxonomy)
  css.addAfterRule(colorSelector, colorAfterRule)
}
