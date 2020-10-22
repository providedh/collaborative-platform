export default function(annotation) {
  let isUnification = annotation.locus === 'attribute' && annotation.match === 'sameAs'
  return {isUnification, ...annotation}
}