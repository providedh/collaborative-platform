export default function(annotation) {
  let isUnification = annotation.match === '@sameAs'
  return {isUnification, ...annotation}
}