export default function(annotation) {
  console.log(annotation)
  let isUnification = annotation.match === '@sameAs'
  return {isUnification, ...annotation}
}